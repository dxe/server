"""Proxies requests to Facebook's Graph API for event data."""
import os

from flask import Flask, jsonify
import requests

LOG_LOCATION = "/opt/dxe/logs/facebook"

app = Flask(__name__)
app.config["APPLICATION_ROOT"] = "/facebook"


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def facebook(path):
    payload = {'access_token': os.environ["FACEBOOK_APP_ACCESS_TOKEN"]}
    r = requests.get(
        'https://graph.facebook.com/{}'.format(path),
        params=payload
    )
    return jsonify(r.json())

if __name__ == "__main__":
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            LOG_LOCATION, maxBytes=100000, backupCount=100)
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)
    app.run()
