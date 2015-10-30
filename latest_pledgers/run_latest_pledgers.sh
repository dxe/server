#!/usr/bin/env bash
cd /opt/dxe/
. /opt/dxe/latest_pledgers/conf.sh
gunicorn --bind 0.0.0.0:8003 latest_pledgers.latest_pledgers:app
