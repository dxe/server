"""Back up the Airtable base."""
import datetime
import os
import tempfile
import urllib
import zipfile

from boto.s3.connection import S3Connection
from boto.s3.key import Key
import requests

AIRTABLE_API_KEY = os.environ["AIRTABLE_API_KEY"]
AIRTABLE_BASE_ID = os.environ["AIRTABLE_BASE_ID"]
S3_BUCKET = "dxe-backup"
S3_BACKUP_DIR = "airtable"
S3_ACCESS_KEY = os.environ["AIRTABLE_BACKUP_AWS_ACCESS_KEY_ID"]
S3_SECRET_KEY = os.environ["AIRTABLE_BACKUP_AWS_SECRET_ACCESS_KEY"]


TABLES = [
    "All Members",
    "Chapters",
    "Events",
    "Working Groups",
]


def get_all_records(table, view):
    headers = {"Authorization": "Bearer {}".format(AIRTABLE_API_KEY)}
    payload = {"view": view, "limit": 100}
    url = "https://api.airtable.com/v0/{}/{}".format(AIRTABLE_BASE_ID, urllib.quote(table))
    records = []
    offset = ""
    while offset is not None:
        r = requests.get(url, headers=headers, params=payload)
        j = r.json()
        records += j["records"]
        offset = j.get("offset", None)
        payload["offset"] = offset
    return records


def backup_all_tables():
    output_dir = tempfile.mkdtemp()
    fname = "{}.zip".format(datetime.datetime.now().strftime('base_backup_%Y-%m-%d_%H:%M:%S'))
    fpath = os.path.join(output_dir, fname)
    with zipfile.ZipFile(
        fpath,
        'w',
        compression=zipfile.ZIP_DEFLATED
    ) as zf:
        for table in TABLES:
            records = get_all_records(table, "Main View")
            zf.writestr("{}.json".format(table), str(records))

    conn = S3Connection(S3_ACCESS_KEY, S3_SECRET_KEY)
    b = conn.get_bucket(S3_BUCKET)
    k = Key(b)
    k.key = "airtable/" + fname
    k.set_contents_from_filename(fpath)


if __name__ == "__main__":
    backup_all_tables()
