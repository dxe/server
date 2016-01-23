"""Health endpoint to report the status of all our services/products.

Uptime Robot polls this endpoint and searches for string matches to
see which services are up and which are down. If any are down, it will
send us an email. To distinguish between services, Uptime Robot does a
string match on the entire response, and we've set it up to do a string
match for the success strings like "Success: blah blah". They have to be
mutually unique though, so the success match for one vital can't be
mistaken for another. Therefore if the text of the strings here change,
the Uptime Robot string matching rules would need to be updated.
"""
import datetime
import os

from boto.s3.connection import S3Connection
from flask import Flask, jsonify
import requests


CHAPTER_MAP_TIMING_WINDOW = datetime.timedelta(hours=4)  # Should update every hour
AIRTABLE_BACKUP_TIMING_WINDOW = datetime.timedelta(days=2)  # Should update every 12 hours

S3_BUCKET = "dxe-backup"
S3_BACKUP_DIR = "airtable"
S3_ACCESS_KEY = os.environ["AIRTABLE_BACKUP_AWS_ACCESS_KEY_ID"]
S3_SECRET_KEY = os.environ["AIRTABLE_BACKUP_AWS_SECRET_ACCESS_KEY"]
CHAPTER_DATA_PATH = "/var/www/maps/chapter_data.json"
CHAPTER_MAP_URL = "http://{}/maps/chapter_map.html"
FACEBOOK_DATA_URL = "http://{}/facebook/attending_event"
LATEST_PLEDGERS_URL = "http://{}/pledge/latest_pledgers/{}"
IMPORTANT_LATEST_PLEDGERS_FIELDS = ["Name", "Country", "City", "days_ago"]

LOG_LOCATION = "/opt/dxe/logs/health"

app = Flask(__name__)


def this_server_ip():
    """Get the ip address of this server."""
    try:
        # Using digitalocean's metadata api
        # https://www.digitalocean.com/community/tutorials/an-introduction-to-droplet-metadata
        r = requests.get("http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address", timeout=.5)
        return r.text
    except:
        return "localhost"


def chapter_map_data_updating():
    """Test to see if the chapter map data is updating."""
    try:
        time_since_last_update = datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(CHAPTER_DATA_PATH))
    except os.error:
        return "Failure: unable to read chapter_data.json"
    if time_since_last_update < CHAPTER_MAP_TIMING_WINDOW:
        return "Success: last updated {} ago".format(time_since_last_update)
    return "Failure: last updated {} ago".format(time_since_last_update)


def chapter_map_page_loads():
    """Test to see if the chapter map page loads."""
    try:
        r = requests.get(CHAPTER_MAP_URL.format(this_server_ip()), timeout=1)
        if r.status_code == 200:  # todo yo are there any other good 200s?
            return "Success: map HTTP Response Code {}".format(r.status_code)
        return "Failure: HTTP Response Code {}".format(r.status_code)
    except requests.exceptions.ConnectionError:
        return "Failure: Connection Error"
    except requests.exceptions.Timeout:
        return "Failure: Request Timed Out"


def chapter_map_status():
    return {"name": "Chapter Map", "vitals": [chapter_map_data_updating(), chapter_map_page_loads()]}


def airtable_backup_key_to_dt(s):
    return datetime.datetime.strptime(s, "airtable/base_backup_%Y-%m-%d_%H:%M:%S.zip")


def airtable_backup_recurring():
    """Test to see if the airtable backup is occurring."""
    conn = S3Connection(S3_ACCESS_KEY, S3_SECRET_KEY)
    b = conn.get_bucket(S3_BUCKET)
    last_backup = max([airtable_backup_key_to_dt(k.name) for k in b.list(S3_BACKUP_DIR + "/", "/") if k.name[-1] != "/"])
    time_since_last_backup = datetime.datetime.now() - last_backup
    if time_since_last_backup < AIRTABLE_BACKUP_TIMING_WINDOW:
        return "Success: last backed up {} ago".format(time_since_last_backup)
    return "Failure: last backed up {} ago".format(time_since_last_backup)


def airtable_backup_status():
    return {"name": "Airtable Backup", "vitals": [airtable_backup_recurring()]}


def fb_event_count_present():
    """Test to see if the facebook data endpoint returns an attendance count for events."""
    try:
        r = requests.get(
            FACEBOOK_DATA_URL.format(this_server_ip()),
            params={"event_id": 1697430973810357},
            timeout=1,
        )
        if r.status_code == 200:
            if "count" in r.json():
                return "Success: fb event HTTP Response Code {}, count {}".format(r.status_code, r.json()["count"])
            else:
                return "Failure: count not in response"
        else:
            return "Failure: HTTP Response Code {}".format(r.status_code)
    except requests.exceptions.ConnectionError:
        return "Failure: Connection Error"
    except requests.exceptions.Timeout:
        return "Failure: Request Timed Out after 1 second"
    except:
        return "Failure: Unknown Error"


def facebook_data_status():
    return {"name": "Facebook Event Data", "vitals": [fb_event_count_present()]}


def latest_pledgers_returns_stuff():
    """Test to see if the latest_pledgers endpoint 200s with some names"""
    try:
        r = requests.get(
            LATEST_PLEDGERS_URL.format(this_server_ip(), 1),
            timeout=4,
        )
        if r.status_code == 200:
            if "pledgers" in r.json() and all(
                [field in r.json()["pledgers"][0] for field in IMPORTANT_LATEST_PLEDGERS_FIELDS]
            ):
                return "Success: pledge HTTP Response Code {}, important fields found".format(r.status_code)
            else:
                return "Failure: one of [{}] fields not in pledgers response".format(", ".join(IMPORTANT_LATEST_PLEDGERS_FIELDS))
        else:
            return "Failure: HTTP Response Code {}".format(r.status_code)
    except requests.exceptions.ConnectionError:
        return "Failure: Connection Error"
    except requests.exceptions.Timeout:
        return "Failure: Request Timed Out after 4 seconds"
    except:
        return "Failure: Unknown Error"


def latest_pledgers_status():
    return {"name": "Latest Pledgers", "vitals": [latest_pledgers_returns_stuff()]}


@app.route('/health')
def health():
    return jsonify({"products": [
        chapter_map_status(),
        airtable_backup_status(),
        facebook_data_status(),
        latest_pledgers_status(),
    ]})


if __name__ == "__main__":
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(LOG_LOCATION, maxBytes=100000, backupCount=100)
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)
    app.run()
