"""API to expose the latest Liberation Pledge pledgers."""
import datetime
from oauth2client.client import SignedJwtAssertionCredentials
import os

import gspread
from flask import Flask, jsonify, request
from werkzeug.contrib.cache import SimpleCache

SHEET_ID = os.environ["LIBERATION_PLEDGE_SHEET_ID"]
NUM_PLEDGERS_LIMIT = 11
ENTRY_LENGTH_LIMIT = 20
LOG_LOCATION = "/opt/dxe/logs/latest_pledgers"
CACHE_TIMEOUT = 10800  # 3 hours

HEADERS = [
    "Submitted On",
    "Name",
    "City",
    "Country",
    "Email",
    "Address",
    "Why are you taking this pledge",
    "Checkbox-1",  # "Share to Facebook" checkbox
]
RETURN_HEADERS = [
    "Submitted On",
    "Name",
    "City",
    "Country",
]

app = Flask(__name__)
cache = SimpleCache()


class cached(object):

    def __init__(self, timeout=None):
        self.timeout = timeout or CACHE_TIMEOUT

    def __call__(self, f):
        def decorator(*args, **kwargs):
            response = cache.get(request.path)
            if response is None:
                response = f(*args, **kwargs)
                cache.set(request.path, response, self.timeout)
            return response
        return decorator


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
@cached()
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
    return jsonify({"pledgers": list(reversed(shortened_row_dicts))})  # ordered newest to oldest

if __name__ == "__main__":
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(LOG_LOCATION, maxBytes=100000, backupCount=100)
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)
    app.run()
