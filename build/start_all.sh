#!/bin/sh
# log rotate
nohup terminal_scheduler > /dev/null 2>&1 &
# websocket tunnel
nohup terminal_tunnel_server > /dev/null 2>&1 &
# wsgi api server
/usr/local/bin/gunicorn --config /etc/terminal/gunicorn.py terminal.server.wsgi_server:application
