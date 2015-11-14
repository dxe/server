#!/usr/bin/env bash
cd /opt/dxe/
. /opt/dxe/airtable/conf.sh
gunicorn --bind 0.0.0.0:8001 health.health:app
