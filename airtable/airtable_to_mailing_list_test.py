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
        # check "one"
        found = False
        for m in to_add:
            if m.airtable_id != "one":
                continue
            found = True
            self.assertEqual(m.email, "blah@blah.com")
            self.assertEqual(len(m.chapters_added), 0)
            self.assertEqual(m.chapters_to_add, set(["one_chapter"]))
        self.assertTrue(found)
        # check that "two", "three", and "four" do not exist in to_add.
        for m in to_add:
            if m.airtable_id == "two"   or \
               m.airtable_id == "three" or \
               m.airtable_id == "four":
                self.fail("member {} should not be in to_add".format(m))
        # check "five"
        found = False
        for m in to_add:
            if m.airtable_id != "five":
                continue
            found = True
            self.assertEqual(m.email, "yup@email.com")
            self.assertEqual(m.chapters_added, set(["one"]))
            self.assertEqual(m.chapters_to_add, set(["two", "three"]))
        self.assertTrue(found)

if __name__ == '__main__':
    unittest.main()
