"""Manages dashboard data.
Pulls event data from facebook, saves data as csvs in s3,
loads data into the db, and generates data views."""
import csv
import io
import json
import hashlib
import os
import time

import argparse
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import requests
import psycopg2

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
    """Uses the Facebook Graph API to get group/page's ids from their links"""
    # This uses's the batch request feature
    # (https://developers.facebook.com/docs/graph-api/making-multiple-requests)
    # to make many logical requests within one http request, saving the overhead
    # cost

    ids = []
    for links_subset in chunks(links, 50):  # batch limit is 50
        reqs = ['{{"method":"GET", "relative_url":"{}"}}'.format(link) for link in links_subset]
        batch_req = '[' + ",".join(reqs) + ']'

        r = requests.post(
            "https://graph.facebook.com/v2.5",
            data={"batch": batch_req},
            headers={"Authorization": "Bearer {}".format(os.environ["FACEBOOK_APP_ACCESS_TOKEN"])}
        )
        data = r.json()
        for i, res in enumerate(data):
            community = json.loads(res['body'])['id']
            if community.startswith("http"):
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
            chapter_links.append(fields["Facebook"])
    return list(set(chapter_links))  # some differnent chapters use the same facebook page, remove dups


def get_events(_id):
    """Given the id of a group or page, returns a list of all the events it hosted.
    Events in the form:
        {id: <event id>, start_time: <ISO datetime string>, name: <name>}"""
    events = []
    next_page_url = "https://graph.facebook.com/v2.5/{}/events?fields=id,start_time,name,owner{{id}}".format(_id)
    while next_page_url:
        r = requests.get(
            next_page_url,
            headers={"Authorization": "Bearer {}".format(os.environ["FACEBOOK_APP_ACCESS_TOKEN"])}
        )
        data = r.json()
        if 'data' in data and len(data['data']) > 0:

            # some groups share events they don't host, which get returned here
            events += [d for d in data['data'] if d['owner']['id'] == _id]

            next_page_url = data['paging'].get('next')
        else:
            next_page_url = False
    for e in events:
        del e["owner"]
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
        if 'data' in data and len(data['data']) > 0:
            users += [d['id'] for d in data['data']]
            next_page_url = data['paging'].get('next')
        else:
            next_page_url = False
    return users


def write_string_to_s3(bucket, key, s):
    """Write the string s to s3 at s3://<bucket>/<key>"""
    k = Key(bucket)
    k.key = key
    k.set_contents_from_string(s)


def rowdicts_to_csv_string(fields, rowdicts):
    """Convert a list of row dicts to a csv string with a header row.
    Only converts the columns listed in `fields`."""
    strout = io.BytesIO()
    writer = csv.DictWriter(strout, delimiter=',', fieldnames=fields)
    writer.writeheader()
    for row in rowdicts:
        writer.writerow({k:v.encode('utf8') for k,v in row.items()})
    return strout.getvalue()


def get_community_events(community_ids):
    """Given a list of fb object ids of groups or pages,
    return all the events hosted by those communities."""
    all_events = []
    for id_ in community_ids:
        community_events = get_events(id_['id'])
        for e in community_events:
            e["community_id"] = id_['id']
        all_events.extend(community_events)

    events = []
    events_so_far = set()
    for e in all_events:
        if e['id'] not in events_so_far:  # some single events are hosted by multiple chapters, throw out one host arbitrarily
            events_so_far.add(e['id'])
            events.append(e)
    return events


def get_attendances(events):
    """Given a list of events, return all the attendees of those events."""
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
    return attendances


def load_to_db(data, columns, table_name, cursor):
    """Load data into the database.
    Args:
        data: list of row dicts with the data to be loaded
        columns: list of columns in the row dicts and table to be loaded
        table_name: name of the table into which the data is loaded
        cursor: psycopg2.cursor object on the db into which the data is loaded"""
    query_with_fields = "INSERT INTO %s (%s) VALUES (%s)" % (table_name, ",".join(columns), ",".join(["%s" for _ in columns]))
    for row_dict in data:
        row = [row_dict[col] for col in columns]
        cursor.execute(query_with_fields, row)


def pull_fb_data():
    """Pulls data from the Facebook Graph API, saves csvs of the data in s3,
    and then loads it into the db."""
    datestr = time.strftime("%m-%d-%y")

    conn = S3Connection(S3_ACCESS_KEY, S3_SECRET_KEY)
    bucket = conn.get_bucket(S3_BUCKET)

    conn = psycopg2.connect(os.environ["DB_STRING"])
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE community, event, attendance CASCADE")

    chapter_links = get_facebook_chapter_links()
    community_ids = [{"id": i} for i in links_to_ids(chapter_links)]
    s = rowdicts_to_csv_string(["id"], community_ids)
    write_string_to_s3(bucket, S3_BACKUP_DIR + "/{}/communities.csv".format(datestr), s)
    load_to_db(community_ids, ["id"], "community", cur)
    conn.commit()

    events = get_community_events(community_ids)
    s = rowdicts_to_csv_string(["id", "name", "start_time", "community_id"], events)
    write_string_to_s3(bucket, S3_BACKUP_DIR + "/{}/events.csv".format(datestr), s)
    load_to_db(events, ["id", "name", "start_time", "community_id"], "event", cur)
    conn.commit()

    attendances = get_attendances(events)
    s = rowdicts_to_csv_string(["id", "event_id", "rsvp_status"], attendances)
    write_string_to_s3(bucket, S3_BACKUP_DIR + "/{}/attendances.csv".format(datestr), s)
    load_to_db(attendances, ["id", "event_id", "rsvp_status"], "attendance", cur)
    conn.commit()


def generate_views(output_dir):
    """Generates data views from the data and outputs it into csvs at `output_dir`."""
    conn = psycopg2.connect(os.environ["DB_STRING"])
    cur = conn.cursor()
    with open(output_dir + "/monthly_attendees.csv", 'w') as f:
        cur.copy_expert("""
COPY
  (SELECT
    to_char(e.start_time, 'YYYY-MM') as monthyear,
    count(*) as num_attendees
  FROM
    event e
  JOIN
    attendance a
  ON
    e.id=a.event_id
  GROUP BY
    monthyear
  ORDER BY
    monthyear)
TO STDOUT
WITH CSV HEADER""", f)
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pull data from fb to the db and generate csv views from that data")
    parser.add_argument("--pull-from-fb", dest='pull_data', action='store_true', default=False, help="Update the db from the fb api", required=False)
    parser.add_argument("--output-dir", dest='output_dir', type=str, help="Directory in which to output the csv views.", required=False)
    args = parser.parse_args()
    if args.pull_data:
        pull_fb_data()
    if args.output_dir:
        generate_views(args.output_dir)
