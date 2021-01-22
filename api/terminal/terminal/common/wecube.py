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


class WeCubeClient(utils.ClientMixin):
    """WeCube Client"""
    def __init__(self, server, token=None):
        self.server = server.rstrip('/')
        self.token = token or utils.get_token()

    def update(self, url_path, data):
        url = self.server + url_path
        return self.post(url, data)

    def retrieve(self, url_path):
        url = self.server + url_path
        return self.get(url)
