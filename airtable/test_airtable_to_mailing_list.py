"""Test airtable_to_mailing_list.py"""
from airtable_to_mailing_list import *
import unittest

class TestAirtableToMailinglist(unittest.TestCase):
    def test_create_chapter_to_mailing_list(self):
        chapters = [{"id": "one", "fields": {"Mailing List Email": "one@email.com"}},
                    {"id": "two"}]
        c_t_ml = create_chapter_to_mailing_list(chapters)
        self.assertEqual(c_t_ml, {"one": "one@email.com"})

    def test_get_members_to_add(self):
        members = [
            {
                "id": "one",
                "fields": {
                    "email": "blah@blah.com",
                    CHAPTER_ID_COL: ["one_chapter"]
                }
            },
            {
                "id": "two",
                "fields": {
                    "email": "nah@gmail.com",
                    CHAPTER_ID_COL: ["two_chapter"],
                    ADDED_TO_MAILING_LIST_COL: ["two_chapter"]
                }
            },
            {
                "id": "three",
                "fields": {
                    "email": "nope@email.com",
                    CHAPTER_ID_COL: ["three_chapter"],
                    OPTED_OUT_COL: True
                }
            },
            {
                "id": "four",
                "fields": {
                    CHAPTER_ID_COL: ["four_chapter"]
                }
            },
            {
                "id": "five",
                "fields": {
                    "email": "yup@email.com",
                    CHAPTER_ID_COL: ["one", "two", "three"],
                    ADDED_TO_MAILING_LIST_COL: ["one"]
                }
            }
        ]
        to_add = get_members_to_add(members)
        to_add_dict = {}
        for m in to_add:
            if m.airtable_id in to_add_dict:
                self.fail("member {} should not be in to_add twice: {}".format(m, to_add))
            to_add_dict[m.airtable_id] = m
        self.assertEqual(to_add_dict,
                         {"one": AddMember(airtable_id="one",
                                           email="blah@blah.com",
                                           chapters_added=set([]),
                                           chapters_to_add=set(["one_chapter"])),
                          "five": AddMember(airtable_id="five",
                                           email="yup@email.com",
                                           chapters_added=set(["one"]),
                                           chapters_to_add=set(["two", "three"]))})


if __name__ == '__main__':
    unittest.main()
