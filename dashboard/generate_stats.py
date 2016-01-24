"""Generate the json data to feed the dashboard view
Usage:
    python generate_stats.py <output file>"""
import csv
import io
import json
import hashlib
import os
import time

from boto.s3.connection import S3Connection
from boto.s3.key import Key
import requests

from airtable.airtable import get_all_records

S3_BUCKET = "dxe-backup"
S3_BACKUP_DIR = "dashboard"
S3_ACCESS_KEY = os.environ["AIRTABLE_BACKUP_AWS_ACCESS_KEY_ID"]
S3_SECRET_KEY = os.environ["AIRTABLE_BACKUP_AWS_SECRET_ACCESS_KEY"]


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def links_to_ids(links):
    """Uses the Facebook Graph API to get the group/page's id from their link"""

    # This uses's the batch request feature
    # (https://developers.facebook.com/docs/graph-api/making-multiple-requests)
    # to make many logical requests within one http request, saving the overhead
    # cost

    ids = []
    links = links[:49]
    for links_subset in chunks(links, 50):  # batch limit is 50
        reqs = ['{{"method":"GET", "relative_url":"{}"}}'.format(link) for link in links]
        batch_req = '[' + ",".join(reqs) + ']'

        r = requests.post(
            "https://graph.facebook.com/v2.5",
            data={"batch": batch_req},
            headers={"Authorization": "Bearer {}".format(os.environ["FACEBOOK_APP_ACCESS_TOKEN"])}
        )
        data = r.json()
        for res in data:
            community = json.loads(res['body'])['id']
            if community[0] == 'h':
                # If the id here is actually a link, then that means it was a fb group. If it's an
                # id, then it was a fb page. The response format is different for each.
                community = json.loads(res['body'])['og_object']['id']
            ids.append(community)
    return ids


def get_facebook_chapter_links():
    """Grab the facebook links for each local chapter from airtable."""
    raw_data = get_all_records("Chapters", "Main View")
    chapter_links = []
    for row in raw_data:
        fields = row["fields"]
        if "Facebook" in fields:
            try:
                chapter_links.append(fields["Facebook"])
            except:
                # TODO: log it, error it, email it, something like that
                pass
    return chapter_links


def get_events(_id):
    """Given the id of a group or page, returns a list of all the events it hosted.
    Events in the form:
        {id: <event id>, start_time: <ISO datetime string>}"""
    events = []
    next_page_url = "https://graph.facebook.com/v2.5/{}/events?fields=id,start_time,name".format(_id)
    while next_page_url:
        r = requests.get(
            next_page_url,
            headers={"Authorization": "Bearer {}".format(os.environ["FACEBOOK_APP_ACCESS_TOKEN"])}
        )
        data = r.json()
        if 'data' in data and len(data['data']) > 0:
            events += data['data']
            next_page_url = data['paging'].get('next')
        else:
            next_page_url = False
    return events


def get_event_participants(_id, rsvp_type):
    """Given the _id of an event, returns a list of all the ids of the fb users
    who RSVP'd either 'interested', 'attending', or 'declined'."""
    if rsvp_type not in ('interested', 'attending', 'declined'):
        raise ValueError("rsvp_type must be in ('interested', 'attending', 'declined')")

    users = []
    next_page_url = "https://graph.facebook.com/v2.5/{}/{}?fields=id".format(_id, rsvp_type)
    while next_page_url:
        r = requests.get(
            next_page_url,
            headers={"Authorization": "Bearer {}".format(os.environ["FACEBOOK_APP_ACCESS_TOKEN"])}
        )
        data = r.json()
        users += [d['id'] for d in data['data']]
        if 'data' in data and len(data['data']) > 0:
            next_page_url = data['paging'].get('next')
        else:
            next_page_url = False
    return users


def count_unique_participants(chapter_ids):
    """Counts the number of unique fb users who RSVP'd positively to any of the
    events under the given groups."""
    # "events{attending{id},interested{id}}"
    pass


def write_string_to_s3(bucket, key, s):
    k = Key(bucket)
    k.key = s
    k.set_contents_from_string(s)


def rowdicts_to_csv_string(fields, rowdicts):
    strout = io.BytesIO()
    writer = csv.DictWriter(strout, delimiter=',', fieldnames=fields)
    writer.writeheader()
    for row in rowdicts:
        writer.writerow({k:v.encode('utf8') for k,v in row.items()})
    return strout.getvalue()


if __name__ == "__main__":
    # get all the urls and names from airtable
    # convert those to fbids, dump (fbid) to csv
    chapter_links = get_facebook_chapter_links()
    chapter_ids = [{"id": i} for i in links_to_ids(chapter_links)]

    datestr = time.strftime("%d-%m-%y")

    conn = S3Connection(S3_ACCESS_KEY, S3_SECRET_KEY)
    bucket = conn.get_bucket(S3_BUCKET)

    s = rowdicts_to_csv_string(["id"], chapter_ids)
    write_string_to_s3(bucket, S3_BACKUP_DIR + "/{}/communities.csv".format(datestr), s)

    # OKAY let's turn those ids into events, then dump those to csv
    events = []
    for id_ in chapter_ids:
        chapter_events = get_events(id_)
        for e in chapter_events:
            e["community_id"] = id_
        events.extend(chapter_events)

    # write to s3 file
    s = rowdicts_to_csv_string(["id", "name", "start_time", "community_id"], events)
    write_string_to_s3(bucket, S3_BACKUP_DIR + "/{}/events.csv".format(datestr), s)

    # TODO remove this shit
    events = [events[0]]

    attendances = []
    for e in events:
        attending_users = [{"id": p} for p in get_event_participants(e["id"], "attending")]
        for p in attending_users:
            p["event_id"] = e["id"]
            p["rsvp_status"] = "attending"
        attendances.extend(attending_users)
        interested_users = [{"id": p} for p in get_event_participants(e["id"], "interested")]
        for p in interested_users:
            p["event_id"] = e["id"]
            p["rsvp_status"] = "interested"
        attendances.extend(interested_users)
    for a in attendances:
        a["id"] = hashlib.sha224(a["id"]).hexdigest()  # don't want to know who is who, just that they're unique

    # write to s3 file
    s = rowdicts_to_csv_string(["id", "event_id", "rsvp_status"], attendances)
    write_string_to_s3(bucket, S3_BACKUP_DIR + "/{}/attendances.csv".format(datestr), s)
