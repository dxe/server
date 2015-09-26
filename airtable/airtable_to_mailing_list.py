"""Sync from Airtable to Google Group mailing lists."""

import httplib2
import json
import airtable
from apiclient.errors import HttpError
from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
from collections import namedtuple

def get_directory():
    with open("../config/client_secret.json") as f:
        secret = json.load(f)
    credentials = SignedJwtAssertionCredentials(secret["client_email"], secret["private_key"], ["https://www.googleapis.com/auth/admin.directory.group"], sub="samer@directactioneverywhere.com")
    http = credentials.authorize(httplib2.Http())
    return build("admin", "directory_v1", http=http)


def create_chapter_to_mailing_list(chapters):
    """Map chapter ids to mailing list emails.

    Takes a list of airtable chapters (that have the form "{ 'id':
    string, 'fields': { 'Mailing List Email': optional string } }")
    and returns a dictionary that maps chapter ids to mailing list
    emails.
    """
    chapter_to_mailing_list = {}
    email_col_name = "Mailing List Email"
    for c in chapters:
        if "fields" in c and email_col_name in c["fields"]:
            email = c["fields"][email_col_name]
            # Sanity check that the email is probably valid.
            if "@" not in email:
                raise Exception("Mailing list email for chapter {} is malformed: {}".format(c, email))
            c_id = c["id"]
            chapter_to_mailing_list[c_id] = email
    return chapter_to_mailing_list


# AddMember is a namedtuple for airtable members.
#  - "airtable_id" is the member's airtable id
#  - "email" is the member's email
#  - "chapters_added" is a list of chapter ids where the member has been
# added to the chapter mailing list
#  - "chapters_to_add" is a list of chapter ids that represents the
# chapters that the member hasn't been added to the mailing list for.
AddMember = namedtuple("AddMember", ["airtable_id", "email", "chapters_added", "chapters_to_add"])

CHAPTER_ID_COL = "chapter_id"
OPTED_OUT_COL = "Opted Out Of Communication"
ADDED_TO_MAILING_LIST_COL = "(DO NOT MODIFY) Added To Mailing List"

def get_members_to_add(members):
    """Filters out members that do not need to be added to a mailing list.

    Filters a list of airtable members that have the form:

    {
    "id": string,
    "fields": {
              "email": optional string,
              "chapter_id": optional list of strings,
              "(DO NOT MODIFY) Added To Mailing List": optional list of strings,
              "Opted Out Of Communication": optional bool
             }
    }

    and filters out the members that have 1) opted out of communication,
    and 2) do not need to be added to a mailing list. Returns a list of
    AddMembers that need to be added to mailing lists.
    """
    members_to_add = []
    for m in members:
        if "fields" not in m:
            continue # m has no fields.
        fields = m["fields"]
        # Skip m if they should not be added to a mailing list because
        # they opted out of communication or they do not have an
        # email.
        if fields.get(OPTED_OUT_COL, False) or "email" not in fields:
            continue
        chapters = set(fields.get(CHAPTER_ID_COL, []))
        chapters_added = set(fields.get(ADDED_TO_MAILING_LIST_COL, []))
        chapters_to_add = chapters - chapters_added
        if not chapters_to_add:
            continue # m is in all the mailing lists that they belong to.
        members_to_add.append(AddMember(airtable_id=m["id"],
                                        email=fields["email"],
                                        chapters_added=chapters_added,
                                        chapters_to_add=chapters_to_add))
    return members_to_add


def sync_airtable_to_mailing_list():
    # chapters is all of the chapters in the "Chapters" table.
    chapters = airtable.get_all_records("Chapters", "Main View")
    if not chapters:
        raise Exception("Expected chapter to not be empty")
    chapter_to_mailing_list = create_chapter_to_mailing_list(chapters)
    if not chapter_to_mailing_list:
        raise Exception("Expected chapter_to_mailing_list to not be empty")
    members = airtable.get_all_records("All Members", "Main View")
    if not members:
        raise Exception("Expected members to not be empty")
    members_to_add = get_members_to_add(members)
    errors = []
    directory = get_directory()
    for m in members_to_add:
        valid_chapters_to_add = []
        for c in m.chapters_to_add:
            if c not in chapter_to_mailing_list:
                continue
            ml = chapter_to_mailing_list[c]
            try:
                directory.members().insert(groupKey=ml, body={"email": m.email.strip()}).execute()
                valid_chapters_to_add.append(c)
            except HttpError as e:
                print e
                content = json.loads(e.content)
                if "Member already exists" in content["error"]["message"]:
                    # Add member if the error is that they already exist.
                    valid_chapters_to_add.append(c)
                    print "Adding member to {} in Airtable anyway.".format(c)
        if not valid_chapters_to_add:
            continue # Don't update the member if they weren't added to any chapter mailing lists.
        # Update member in airtable.
        valid_chapters_to_add += m.chapters_added
        r = airtable.update_record("All Members", m.airtable_id, {ADDED_TO_MAILING_LIST_COL: valid_chapters_to_add})
        if r.status_code != 200:
            raise Exception("Expected '200' from airtable.update_record: {}, {}, {}".format(m.airtable_id, valid_chapters_to_add, r.text))
    print "done!"


if __name__ == "__main__":
    sync_airtable_to_mailing_list()
