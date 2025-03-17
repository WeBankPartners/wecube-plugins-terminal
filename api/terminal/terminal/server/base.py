# coding=utf-8
"""
terminal.server.base
~~~~~~~~~~~~~~~~~~~~

本模块提供wsgi启动前数据处理能力

"""

from __future__ import absolute_import

import os
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA
from urllib.parse import quote_plus

from talos.core import config

from terminal.common import utils as plugin_utils

RSA_KEY_PATH = '/certs/rsa_key'


def decrypt_rsa(secret_key, encrypt_text):
    rsakey = RSA.importKey(secret_key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    random_generator = Random.new().read
    text = cipher.decrypt(plugin_utils.b64decode_key(encrypt_text), random_generator)
    return text.decode('utf-8')


@config.intercept('db_username', 'db_hostip', 'db_hostport', 'db_schema', 'gateway_url', 'asset_type',
                  'asset_field_name', 'asset_field_ip', 'asset_field_user', 'asset_field_password', 'asset_field_port',
                  'asset_field_desc', 'jwt_signing_key', 'boxes_check', 'sub_system_code', 'sub_system_key',
                  'websocket_url', 'session_timeout', 'platform_timezone', 'check_itsdangerous', 'download_max_size',
                  'platform_encrypt_seed', 's3_server_url', 's3_access_key', 's3_secret_key', 's3_bucket', 'mode',
                  'log_level')
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


@config.intercept('db_password')
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
        new_value = quote_plus(new_value)
        return new_value
    value = quote_plus(value)
    return value