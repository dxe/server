"""API to expose the latest Liberation Pledge pledgers."""
import datetime
from oauth2client.client import SignedJwtAssertionCredentials
import os

import gspread
from flask import Flask, jsonify

SHEET_ID = os.environ["LIBERATION_PLEDGE_SHEET_ID"]
NUM_PLEDGERS_LIMIT = 50
ENTRY_LENGTH_LIMIT = 20

HEADERS = [
    "Submitted On",
    "Name",
    "Email Address",
    "I pledge to",  # unused
    "Comment",
    "City",
    "Country",
    "Share to facebook",  # unused
    "Checkbox-1",  # new "I pledge to ..." checkbox
    "Checkbox-2",  # new "Share to Facebook" checkbox
    "Why are you taking this pledge",

]
RETURN_HEADERS = [
    "Submitted On",
    "Name",
    "City",
    "Country",
]

app = Flask(__name__)


def get_gspread_client():
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = SignedJwtAssertionCredentials(
        os.environ["GOOGLE_API_CLIENT_EMAIL"],
        os.environ["GOOGLE_API_PRIVATE_KEY"],
        scope
    )
    return gspread.authorize(credentials)
gc = get_gspread_client()


def shorten_field(field):
    if len(field) >= ENTRY_LENGTH_LIMIT:
        return field[:ENTRY_LENGTH_LIMIT - 3] + "..."
    return field


@app.route('/pledge/latest_pledgers/<int:num>')
def latest_pledgers(num):
    """Returns the last `num` pledgers."""
    if num < 1:
        return jsonify({"error": "number of entries requested must be a positive integer"})
    elif num > NUM_PLEDGERS_LIMIT:
        return jsonify({"error": "number of entries requested too high"})

    global gc
    try:
        sheet = gc.open_by_key(SHEET_ID).sheet1
    except:
        gc = get_gspread_client()
        sheet = gc.open_by_key(SHEET_ID).sheet1

    if sheet.row_count - 1 < num:  # There aren't `num` pledgers (-1 for header row)
        latest_values = sheet.get_all_values()[1:]
    else:
        latest_values = sheet.get_all_values()[-num:]

    row_dicts = [dict(zip(HEADERS, row)) for row in latest_values]
    cleaned_row_dicts = [{k: v for k, v in row.iteritems() if k in RETURN_HEADERS} for row in row_dicts]
    shortened_row_dicts = [{k: shorten_field(v) for k, v in row.iteritems()} for row in cleaned_row_dicts]
    for row_dict in shortened_row_dicts:
        days_ago = (datetime.datetime.now() - datetime.datetime.strptime(row_dict["Submitted On"], "%m/%d/%Y %H:%M:%S")).days
        if days_ago <= 0:
            days_ago_str = "Today"
        elif days_ago == 1:
            days_ago_str = "{} day ago".format(days_ago)
        else:  # days_ago >= 2
            days_ago_str = "{} days ago".format(days_ago)

        row_dict["days_ago"] = days_ago_str
    return jsonify({"pledgers": shortened_row_dicts})

if __name__ == "__main__":
    app.run()
