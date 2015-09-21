"""Interface with Airtable"""
import json
import os
import urllib

import requests

AIRTABLE_API_KEY = os.environ["AIRTABLE_API_KEY"]
AIRTABLE_BASE_ID = os.environ["AIRTABLE_BASE_ID"]

TABLES = [
    "All Members",
    "Chapters",
    "Events",
    "Working Groups",
]


def get_url(table):
    return "https://api.airtable.com/v0/{}/{}".format(AIRTABLE_BASE_ID, urllib.quote(table))


def update_record(table, row_id, fields_dict):
    """Update a single airtable record."""
    headers = {"Authorization": "Bearer {}".format(AIRTABLE_API_KEY),
               "Content-type": "application/json"}
    url = get_url(table) + "/" + row_id
    data = json.dumps({"fields": fields_dict})
    return requests.patch(url, headers=headers, data=data)


def get_all_records(table, view):
    """Return all the records for an Airtable table and view.

    The records have the fields "id", "fields", and "createdTime".
    """
    headers = {"Authorization": "Bearer {}".format(AIRTABLE_API_KEY)}
    payload = {"view": view, "limit": 100}
    url = get_url(table)
    records = []
    offset = ""
    while offset is not None:
        r = requests.get(url, headers=headers, params=payload)
        j = r.json()
        records += j["records"]
        offset = j.get("offset", None)
        payload["offset"] = offset
    return records
