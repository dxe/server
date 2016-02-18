"""Proxies requests to Facebook's Graph API for event data."""
import os

from flask import Flask, jsonify, request
import requests

LOG_LOCATION = "/opt/dxe/logs/facebook"

app = Flask(__name__)


@app.route("/facebook/attending_event")
def attending_event():
    """Get the number of people who have replied 'attending' or 'maybe' to an event by event_id."""
    event_id = request.args["event_id"]
    r = requests.get(
        "https://graph.facebook.com/v2.5/{}".format(event_id),
        params={"fields": "id,attending_count,maybe_count"},
        headers={"Authorization": "Bearer {}".format(os.environ["FACEBOOK_APP_ACCESS_TOKEN"])}
    )
    data = r.json()
    return jsonify({"count": data["attending_count"] + data["maybe_count"]})


if __name__ == "__main__":
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(LOG_LOCATION, maxBytes=100000, backupCount=100)
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)
    app.run()
