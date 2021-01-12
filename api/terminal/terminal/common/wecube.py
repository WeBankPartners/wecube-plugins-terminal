# coding=utf-8
"""
terminal.common.wecube
~~~~~~~~~~~~~~~~~~~~~~

本模块提供项目WeCube Client（Proxy）

"""
import logging

from talos.common import cache
from talos.core import config
from talos.core.i18n import _
from talos.core import utils as talos_utils
from talos.utils import scoped_globals
from terminal.common import exceptions
from terminal.common import utils

LOG = logging.getLogger(__name__)
CONF = config.CONF
WECUBE_TOKEN = 'wecube_platform_token'


def get_wecube_token(base_url=None):
    base_url = base_url or CONF.wecube.base_url
    token = talos_utils.get_attr(scoped_globals.GLOBALS, 'request.auth_token') or CONF.wecube.token
    if not CONF.wecube.use_token:
        token = cache.get(WECUBE_TOKEN)
        if not cache.validate(token):
            token = utils.RestfulJson.post(base_url + '/auth/v1/api/login',
                                           json={
                                               "username": CONF.wecube.username,
                                               "password": CONF.wecube.password
                                           }).json()['data'][1]['token']
            cache.set(WECUBE_TOKEN, token)
    return token


class WeCubeClient(object):
    """WeCube Client"""
    def __init__(self, server, token=None):
        self.server = server.rstrip('/')
        self.token = token or get_wecube_token(self.server)

    def build_headers(self):
        return {'Authorization': 'Bearer ' + self.token}

    def check_response(self, resp_json):
        if resp_json['status'] != 'OK':
            # 当创建/更新条目错误，且仅有一个错误时，返回内部错误信息
            if isinstance(resp_json.get('data', None), list) and len(resp_json['data']) == 1:
                if 'message' in resp_json['data'][0]:
                    raise exceptions.PluginError(message=resp_json['data'][0]['message'])
            raise exceptions.PluginError(message=resp_json['message'])

    def get(self, url, param=None):
        LOG.info('GET %s', url)
        LOG.debug('Request: query - %s, data - None', str(param))
        resp_json = utils.RestfulJson.get(url, headers=self.build_headers(), params=param)
        LOG.debug('Response: %s', str(resp_json))
        self.check_response(resp_json)
        return resp_json

    def post(self, url, data, param=None):
        LOG.info('POST %s', url)
        LOG.debug('Request: query - %s, data - %s', str(param), str(data))
        resp_json = utils.RestfulJson.post(url, headers=self.build_headers(), params=param, json=data)
        LOG.debug('Response: %s', str(resp_json))
        self.check_response(resp_json)
        return resp_json

    def update(self, url_path, data):
        url = self.server + url_path
        return self.post(url, data)

    def retrieve(self, url_path):
        url = self.server + url_path
        return self.get(url)
