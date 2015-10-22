cd /opt/dxe/
. /opt/dxe/facebook/conf.sh
gunicorn --bind 0.0.0.0:8002 facebook.facebook:app
