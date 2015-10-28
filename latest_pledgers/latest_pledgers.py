"""API to expose the latest Liberation Pledge pledgers."""
from oauth2client.client import SignedJwtAssertionCredentials
import os

import gspread
from flask import Flask, jsonify

SHEET_ID = os.environ["LIBERATION_PLEDGE_SHEET_ID"]
NUM_PLEDGERS_LIMIT = 50
HEADERS = [
    "Submitted On",
    "Name",
    "Email Address",
    "I pledge to",
    "Comment",
]
RETURN_HEADERS = [
    "Submitted On",
    "Name",
    "Comment",
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


@app.route('/pledge/latest_pledgers/<int:num>')
def health(num):
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
    return jsonify({"pledgers": cleaned_row_dicts})

if __name__ == "__main__":
    app.debug = True
    app.run()
