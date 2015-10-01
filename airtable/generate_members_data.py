"""Generate the json data for the attendance page from Airtable
Usage:
    python generate_members_data.py <output file>
"""
import json
import re
import sys

from backup_airtable import get_all_records


def get_members_data():
    raw_data = get_all_records("All Members", "Main View")
    ret = {}
    ret["All Members:Main View"] = [] 
    for row in raw_data:
        fields = row["fields"]
        if "first_name" in fields or "last_name" in fields:
            retrow = { "fields":{} }
            retrow["fields"]["first_name"] = fields.get("first_name")
            retrow["fields"]["last_name"]  = fields.get("last_name")
            retrow["fields"]["chapter_id"]  = fields.get("chapter_id")
            retrow["id"] = row["id"]
            ret["All Members:Main View"].append(retrow)
        else:
            # well we can't really do anything without a name...
            pass
    row_data = get_all_records("Chapters", "Main View")
    ret["Chapters:Main View"] = [] 
    for row in row_data:
        fields = row["fields"]
        if "Name" in fields:
            retrow = { "fields":{} }
            retrow["fields"]["Name"]        = fields.get("Name")
            retrow["fields"]["All Members"] = fields.get("All Members")
            retrow["id"] = row["id"]
            ret["Chapters:Main View"].append(retrow) 
    return ret


if __name__ == "__main__":
    data = get_members_data()
    with open(sys.argv[1], "w") as f:
        json.dump(data, f, indent=4)
