# coding=utf-8
"""
terminal.server.wsgi_server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供wsgi启动能力

"""

from __future__ import absolute_import

import os
import json
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA
from talos.server import base
from talos.core import utils
from talos.core import config

from terminal.common import utils as plugin_utils
from terminal.middlewares import auth
from terminal.middlewares import permission

RSA_KEY_PATH = '/certs/rsa_key'


def decrypt_rsa(secret_key, encrypt_text):
    rsakey = RSA.importKey(secret_key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    random_generator = Random.new().read
    text = cipher.decrypt(plugin_utils.b64decode_key(encrypt_text), random_generator)
    return text.decode('utf-8')


@config.intercept('db_username', 'db_password', 'db_hostip', 'db_hostport', 'db_schema', 'gateway_url', 'asset_type',
                  'asset_field_name', 'asset_field_ip', 'asset_field_user', 'asset_field_password', 'asset_field_port',
                  'asset_field_desc', 'jwt_signing_key')
def get_env_value(value, origin_value):
    prefix = 'ENV@'
    encrypt_prefix = 'RSA@'
    if value.startswith(prefix):
        env_name = value[len(prefix):]
        new_value = os.getenv(env_name, default='')
        if new_value.startswith(encrypt_prefix):
            certs_path = RSA_KEY_PATH
            if os.path.exists(certs_path) and os.path.isfile(certs_path):
                with open(certs_path) as f:
                    new_value = decrypt_rsa(f.read(), new_value[len(encrypt_prefix):])
            else:
                raise ValueError('keys with "RSA@", but rsa_key file not exists')
        return new_value
    return value


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
