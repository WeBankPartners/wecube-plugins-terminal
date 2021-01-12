# coding=utf-8

from __future__ import absolute_import

import logging
from talos.core import config
from talos.db.crud import ResourceBase
from terminal.common import wecmdb
from terminal.common import utils
from terminal.common import exceptions

CONF = config.CONF
LOG = logging.getLogger(__name__)


class Asset(object):
    def _transform_field(self, datas, fields):
        results = []
        for item in datas:
            new_item = {}
            for origin_name, name in fields.items():
                new_item[name] = item.get(origin_name, None)
            results.append(new_item)
        return results

    def get_connection_info(self, rid):
        counter, datas = self.list({'id': rid})
        if not counter:
            raise exceptions.NotFoundError(resource='Asset(#%s)' % rid)
        return datas[0]

    def list(self, filters=None, orders=None, offset=None, limit=None, hooks=None):
        fields = {
            'id': 'id',
            'name': 'name',
            'display_name': 'display_name',
            'ip_address': 'ip_address',
            'username': 'username',
            'password': 'password',
            'cpu': 'cpu',
            'memory': 'memory'
        }
        client = wecmdb.WeCMDBClient(CONF.wecube.base_url, utils.get_token())
        query = utils.transform_filter_to_cmdb_query(filters, orders=orders, offset=offset, limit=limit)
        resp_json = client.retrieve(CONF.wecmdb.asset_type, query)
        counter = resp_json.get('data', {}).get('pageInfo', {}).get('totalRows') or 0
        datas = resp_json.get('data', {}).get('contents', [])
        datas = self._transform_field(datas, fields)
        return counter, datas
