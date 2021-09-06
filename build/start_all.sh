#!/bin/sh
# compatible with standalone
mkdir -p /data/terminal/ui
echo "It works" > /data/terminal/ui/index.html
# log rotate
nohup terminal_scheduler > /dev/null 2>&1 &
# websocket tunnel
nohup terminal_tunnel_server > /dev/null 2>&1 &
# s3 uploader worker
nohup terminal_uploader > /dev/null 2>&1 &
# wsgi api server
/usr/local/bin/gunicorn --config /etc/terminal/gunicorn.py terminal.server.wsgi_server:application
