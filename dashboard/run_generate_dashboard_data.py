#!/usr/bin/env bash
export PYTHONPATH='/opt/dxe'
source /opt/dxe/airtable/conf.sh
source /opt/dxe/facebook/conf.sh
source /opt/dxe/dashboard/conf.sh
if [ "$1" = "views_only" ]; then
    /usr/bin/env python /opt/dxe/dashboard/generate_dashboard_data.py \
        --output-dir='/var/www/dashboard/'
else
    /usr/bin/env python /opt/dxe/dashboard/generate_dashboard_data.py \
        --pull-from-fb \
        --output-dir='/var/www/dashboard/'
fi
