# coding=utf-8
"""
terminal.server.wsgi_server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供wsgi启动能力

"""

from __future__ import absolute_import

import os
import json
from talos.server import base
from talos.core import utils

from terminal.middlewares import auth
from terminal.middlewares import permission
from terminal.server import base as terminal_base


def error_serializer(req, resp, exception):
    representation = exception.to_dict()
    # replace code with internal application code
    if 'error_code' in representation:
        representation['code'] = representation.pop('error_code')
    representation['status'] = 'ERROR'
    representation['data'] = representation.get('data', None)
    representation['message'] = representation.pop('description', '')
    resp.body = json.dumps(representation, cls=utils.ComplexEncoder)
    resp.content_type = 'application/json'


application = base.initialize_server('terminal',
                                     os.environ.get('TERMINAL_CONF', '/etc/terminal/terminal.conf'),
                                     conf_dir=os.environ.get('TERMINAL_CONF_DIR', '/etc/terminal/terminal.conf.d'),
                                     middlewares=[auth.JWTAuth(), permission.Permission()])
application.set_error_serializer(error_serializer)
application.req_options.auto_parse_qs_csv = True
