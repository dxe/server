"""Generate the json data for the chapter map from Airtable
Usage:
    python generate_chapter_data.py <output file>"""
import json
import re
import sys
import time

import requests

from airtable import get_all_records

GEOCODING_RETRIES = 4


def get_lat_long(s):
    match = re.search(r'\((\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)\)', s)
    if match:  # it's a lat long
        return float(match.group(1)), float(match.group(3))
    else:  # fuuuuck it's an address, ask google about how to make that a lat long
        payload = {"address": s}
        r = requests.get("http://maps.googleapis.com/maps/api/geocode/json", params=payload).json()

        tries = 1
        while r["status"] == "UNKNOWN_ERROR" and tries < GEOCODING_RETRIES:
            time.sleep(60)  # Hold up one minute please. Google has failed many times in a row for unknown reasons...
            tries += 1
            r = requests.get("http://maps.googleapis.com/maps/api/geocode/json", params=payload).json()
        if r["status"] == "UNKNOWN_ERROR":
            print "Got UNKNOWN_ERROR {} times on address {}. Gave up. Full response:\n{}".format(GEOCODING_RETRIES, s, r)
            return None, None

        if len(r["results"]) > 0:
            loc = r["results"][0]["geometry"]["location"]
            return float(loc["lat"]), float(loc["lng"])
        else:
            # well we can't get a lat long, we give up...
            print "failed to get lat long from address {}. Full response:\n{}".format(s, r)
            return None, None


def get_chapter_data():
    raw_data = get_all_records("Chapters", "Main View")
    ret = []
    for row in raw_data:
        fields = row["fields"]
        if "Name" in fields and "Location" in fields:
            retrow = {}
            lat, lng = get_lat_long(fields["Location"])
            if lat and lng:
                retrow["lat"] = lat
                retrow["long"] = lng
            else:
                continue

            retrow["name"] = fields["Name"]
            retrow["facebook"] = fields.get("Facebook")
            retrow["email"] = fields.get("Contact Email")
            retrow["youtube"] = fields.get("YouTube Channel")
            retrow["organizers"] = fields.get("Organizers Page")
            retrow["calendar"] = fields.get("Calendar")

            # special case: DxE SLC has their own website. They're likely to be
            # the only one to have their own for a while, so it's not worth it
            # to make a new column for website. We'll artificially inject their
            # site here.
            if fields["Name"] == "Salt Lake City":
                retrow["website"] = "http://dxeslc.org/"

            ret.append(retrow)
        else:
            # well we can't really do anything without a name and location...
            pass
    return ret


if __name__ == "__main__":
    data = get_chapter_data()
    with open(sys.argv[1], "w") as f:
        json.dump(data, f, indent=4)
