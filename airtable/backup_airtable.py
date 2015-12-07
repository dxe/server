"""Back up the Airtable base."""
import datetime
import json
import os
import tempfile
import zipfile

from boto.s3.connection import S3Connection
from boto.s3.key import Key
import airtable

S3_BUCKET = "dxe-backup"
S3_BACKUP_DIR = "airtable"
S3_ACCESS_KEY = os.environ["AIRTABLE_BACKUP_AWS_ACCESS_KEY_ID"]
S3_SECRET_KEY = os.environ["AIRTABLE_BACKUP_AWS_SECRET_ACCESS_KEY"]


def backup_all_tables():
    output_dir = tempfile.mkdtemp()
    fname = "{}.zip".format(datetime.datetime.now().strftime('base_backup_%Y-%m-%d_%H:%M:%S'))
    fpath = os.path.join(output_dir, fname)
    with zipfile.ZipFile(
        fpath,
        'w',
        compression=zipfile.ZIP_DEFLATED
    ) as zf:
        for table in airtable.TABLES:
            records = airtable.get_all_records(table, "Main View")
            zf.writestr("{}.json".format(table), json.dumps(records))

    conn = S3Connection(S3_ACCESS_KEY, S3_SECRET_KEY)
    b = conn.get_bucket(S3_BUCKET)
    k = Key(b)
    k.key = S3_BACKUP_DIR + "/" + fname
    k.set_contents_from_filename(fpath)


if __name__ == "__main__":
    backup_all_tables()
