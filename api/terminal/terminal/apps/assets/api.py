# coding=utf-8

from __future__ import absolute_import

import logging
import os.path

from talos.core import config
from talos.core.i18n import _
from terminal.db import resource
from terminal.common import wecmdb
from terminal.common import ssh
from terminal.common import utils
from terminal.common import exceptions

CONF = config.CONF
LOG = logging.getLogger(__name__)


class Asset(object):
    def __init__(self, token=None):
        self._token = token

    def _transform_field(self, datas, fields):
        results = []
        for item in datas:
            new_item = {}
            for origin_name, name in fields.items():
                new_item[name] = item.get(origin_name, None)
            results.append(new_item)
        return results

    def get_connection_info(self, rid):
        datas = self.list({'id': rid})
        if not datas:
            raise exceptions.NotFoundError(resource='Asset(#%s)' % rid)
        return datas[0]

    def list(self, filters=None, orders=None, offset=None, limit=None, hooks=None):
        fields = {
            'id': 'id',
            'name': 'name',
            'displayName': 'display_name',
            'ip_address': 'ip_address',
            'user_name': 'username',
            'user_password': 'password',
            'description': 'description'
        }
        client = wecmdb.EntityClient(CONF.wecube.base_url, self._token or utils.get_token())
        query = utils.transform_filter_to_entity_query(filters, fields_mapping=fields)
        package, entity = CONF.wecmdb.asset_type.split(':')
        resp_json = client.retrieve(package, entity, query)
        datas = resp_json.get('data', [])
        datas = self._transform_field(datas, fields)
        return datas


class AssetFile(object):
    def upload(self, filename, fileobj, destpath, rid):
        asset = Asset().get_connection_info(rid)
        fullpath = os.path.join(destpath, filename)
        client = ssh.SSHClient()
        client.connect(asset['ip_address'], asset['username'], asset['password'])
        sftp = client.create_sftp()
        try:
            sftp.putfo(fileobj, fullpath)
        except FileNotFoundError:
            raise exceptions.ValidationError(message=_('%(filepath)s not exist') % {'filepath': destpath})
        except PermissionError:
            raise exceptions.ValidationError(message=_('upload to %(filepath)s error: permission denied') %
                                             {'filepath': destpath})
        return fullpath

    def download(self, filepath, rid):
        asset = Asset().get_connection_info(rid)
        client = ssh.SSHClient()
        client.connect(asset['ip_address'], asset['username'], asset['password'])
        sftp = client.create_sftp()
        try:
            stat_result = sftp.stat(filepath)
        except FileNotFoundError as e:
            raise exceptions.ValidationError(message=_('%(filepath)s not exist') % {'filepath': filepath})
        stat_result = ssh.SSHClient.format_sftp_attr('./', stat_result)
        if stat_result['type'] != ssh.FileType.T_FILE:
            raise exceptions.ValidationError(message=_('%(filepath)s is not a regular file') % {'filepath': filepath})
        filesize = stat_result['size']
        fileobj = sftp.open(filepath, "rb")
        return fileobj, filesize


TransferRecord = resource.TransferRecord


class SessionRecord(resource.SessionRecord):
    def download(self, rid):
        ref = self.get(rid)
        if ref:
            fullpath = os.path.join(CONF.session.record_path, ref['filepath'])
            if not os.path.exists(fullpath):
                raise exceptions.NotFoundError(resource='File of SessionRecord[%s]' % rid)
            return open(fullpath, 'rb'), os.path.getsize(fullpath)
        else:
            raise exceptions.NotFoundError(resource='SessionRecord[%s]' % rid)


Permission = resource.Permission
