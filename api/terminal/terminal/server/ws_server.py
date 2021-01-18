# coding=utf-8
"""
terminal.server.ws_server
~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供WebSocket服务启动能力

"""

import sys
import asyncio

import tornado.websocket
import tornado.web
import tornado.httpserver
import tornado.options
from talos.core import config
from terminal.common.wshandler import SSHHandler
from terminal.server.wsgi_server import application

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

CONF = config.CONF

settings = {}

app = tornado.web.Application([
    (r"/terminal/v1/ssh", SSHHandler),
], **settings)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(app)
    print('listen on %s:%s...' % (CONF.ws_server.bind, CONF.ws_server.port))
    http_server.listen(CONF.ws_server.port, CONF.ws_server.bind)
    http_server.start(0)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()