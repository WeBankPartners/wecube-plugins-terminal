# coding=utf-8

from __future__ import absolute_import

import os
import jwt
import jwt.exceptions
from talos.core import config
from talos.core import exceptions as base_ex
from terminal.common import utils

CONF = config.CONF


class JWTAuth(object):
    """中间件，提供JWT Token信息解析"""
    def process_request(self, req, resp):
        req.auth_user = None
        req.auth_token = None
        req.auth_permissions = []
        req.auth_client_type = 'USER'
        # 忽略token的接口必须是不需要token信息
        if req.path in CONF.login_passthrough:
            return
        if req.path == '/':
            return
        extensions = req.path.rsplit('.', 1)
        if len(extensions) > 1:
            extension = extensions[1]
            if extension in ['css', 'woff', 'woff2', 'tff', 'svg', 'jpg', 'jpeg', 'png', 'ico', 'js', 'map', 'html']:
                return
        token_header = req.headers.get('Authorization'.upper(), None)
        token_cookie = req.get_cookie_values('accessToken')
        if token_cookie:
            token_header = token_header or 'Bearer ' + token_cookie[0]
        secret = CONF.jwt_signing_key
        if token_header:
            token = token_header[len('Bearer '):]
            req.auth_token = token
            verify_token = False
            if secret:
                verify_token = True
            try:
                decoded_secret = utils.b64decode_key(secret)
                token_info = jwt.decode(token, key=decoded_secret, verify=verify_token)
                req.auth_user = token_info['sub']
                authority = token_info.get('authority', None) or '[]'
                req.auth_permissions = set(authority.strip('[]').split(','))
                req.auth_client_type = token_info.get('clientType', None) or 'USER'
                if verify_token:
                    # delay token
                    token_info['exp'] += 120
                    req.auth_token = jwt.encode(token_info, decoded_secret, algorithm='HS512').decode()
            except jwt.exceptions.ExpiredSignatureError as e:
                raise base_ex.AuthError()
            except jwt.exceptions.DecodeError as e:
                raise base_ex.AuthError()
        else:
            raise base_ex.AuthError()
