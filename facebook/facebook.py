"""Proxies requests to Facebook's Graph API for event data."""
import os

from flask import Flask, jsonify, request
import requests

app = Flask(__name__)


@app.route("/facebook/attending_event")
def attending_event():
    """Get the number of people who have replied 'attending' or 'maybe' to an event by event_id."""
    event_id = request.args["event_id"]
    r = requests.get(
        "https://graph.facebook.com/{}".format(event_id),
        params={"fields": "id,attending_count,maybe_count"},
        headers={"Authorization": "Bearer {}".format(os.environ["FACEBOOK_APP_ACCESS_TOKEN"])}
    )
    data = r.json()
    return jsonify({"count": data["attending_count"] + data["maybe_count"]})


if __name__ == "__main__":
    app.run()
