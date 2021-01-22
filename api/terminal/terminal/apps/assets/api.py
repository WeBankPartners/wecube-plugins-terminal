# coding=utf-8

from __future__ import absolute_import

import datetime
import logging
import os.path

from talos.core import config
from talos.core.i18n import _
from talos.utils.scoped_globals import GLOBALS
from terminal.db import resource
from terminal.common import wecmdb
from terminal.common import ssh
from terminal.common import utils
from terminal.common import exceptions

CONF = config.CONF
LOG = logging.getLogger(__name__)


class Asset(object):
    def __init__(self, token=None):
        self._token = token or utils.get_token()

    def _transform_field(self, datas, fields):
        results = []
        for item in datas:
            new_item = {}
            for origin_name, name in fields.items():
                new_item[name] = item.get(origin_name, None)
            results.append(new_item)
        return results

    def get_connection_info(self, rid, auth_roles=None):
        datas = self.list({'id': rid}, auth_roles=auth_roles)
        if not datas:
            raise exceptions.NotFoundError(resource='Asset(#%s)' % rid)
        return datas[0]

    def list_query(self, filters=None, orders=None, offset=None, limit=None, hooks=None):
        fields = {
            'id': 'id',
            'name': 'name',
            'displayName': 'display_name',
            'ip_address': 'ip_address',
            'user_name': 'username',
            'description': 'description'
        }
        client = wecmdb.EntityClient(CONF.wecube.base_url, self._token)
        query = utils.transform_filter_to_entity_query(filters, fields_mapping=fields)
        package, entity = CONF.wecmdb.asset_type.split(':')
        resp_json = client.retrieve(package, entity, query)
        datas = resp_json.get('data', [])
        datas = self._transform_field(datas, fields)
        return datas

    def list(self, filters=None, orders=None, offset=None, limit=None, hooks=None, auth_roles=None):
        fields = {
            'id': 'id',
            'name': 'name',
            'displayName': 'display_name',
            'ip_address': 'ip_address',
            'user_name': 'username',
            'user_password': 'password',
            'description': 'description'
        }
        client = wecmdb.EntityClient(CONF.wecube.base_url, self._token)
        query = utils.transform_filter_to_entity_query(filters, fields_mapping=fields)
        package, entity = CONF.wecmdb.asset_type.split(':')
        resp_json = client.retrieve(package, entity, query)
        datas = resp_json.get('data', [])
        datas = self._transform_field(datas, fields)
        permissions = resource.Permission().list({
            "roles.role": {
                'in': auth_roles or list(GLOBALS.request.auth_permissions)
            },
            'auth_execute': 1,
            'enabled': 1
        })
        auth_asset_ids = []
        for permission in permissions:
            auth_asset_ids.extend([auth_asset['asset_id'] for auth_asset in permission['assets']])
        auth_asset_ids = set(auth_asset_ids)
        datas = [item for item in datas if item['id'] in auth_asset_ids]
        return datas


class AssetFile(object):
    def upload(self, filename, fileobj, destpath, rid):
        asset = Asset().get_connection_info(rid)
        fullpath = os.path.join(destpath, filename)
        client = ssh.SSHClient()
        client.connect(asset['ip_address'], asset['username'], asset['password'])
        sftp = client.create_sftp()
        record = TransferRecord().create({
            'asset_id': rid,
            'filepath': fullpath,
            'filesize': int(GLOBALS.request.get_header('content-length', None) or 0),
            'user': GLOBALS.request.auth_user,
            'operation_type': 'upload',
            'started_time': datetime.datetime.now()
        })
        try:
            sftp.putfo(fileobj, fullpath)
            TransferRecord().update(record['id'], {'ended_time': datetime.datetime.now(), 'status': 'OK'})
        except FileNotFoundError:
            TransferRecord().update(record['id'], {'ended_time': datetime.datetime.now(), 'status': 'ERROR'})
            raise exceptions.ValidationError(message=_('%(filepath)s not exist') % {'filepath': destpath})
        except PermissionError:
            TransferRecord().update(record['id'], {'ended_time': datetime.datetime.now(), 'status': 'ERROR'})
            raise exceptions.ValidationError(message=_('upload to %(filepath)s error: permission denied') %
                                             {'filepath': destpath})
        return fullpath

    def download(self, filepath, rid):
        # closeable wrapper
        def _close_proxy(func, record):
            def ___close_proxy(*args, **kwargs):
                print('end download', datetime.datetime.now())
                TransferRecord().update(record['id'], {'ended_time': datetime.datetime.now(), 'status': 'OK'})
                return func(*args, **kwargs)

            return ___close_proxy

        asset = Asset().get_connection_info(rid)
        client = ssh.SSHClient()
        client.connect(asset['ip_address'], asset['username'], asset['password'])
        sftp = client.create_sftp()
        record = TransferRecord().create({
            'asset_id': rid,
            'filepath': filepath,
            'filesize': 0,
            'user': GLOBALS.request.auth_user,
            'operation_type': 'download',
            'started_time': datetime.datetime.now()
        })
        print('start download', datetime.datetime.now())
        try:
            stat_result = sftp.stat(filepath)
        except FileNotFoundError as e:
            TransferRecord().update(record['id'], {'ended_time': datetime.datetime.now(), 'status': 'ERROR'})
            raise exceptions.ValidationError(message=_('%(filepath)s not exist') % {'filepath': filepath})
        stat_result = ssh.SSHClient.format_sftp_attr('./', stat_result)
        if stat_result['type'] != ssh.FileType.T_FILE:
            TransferRecord().update(record['id'], {'ended_time': datetime.datetime.now(), 'status': 'ERROR'})
            raise exceptions.ValidationError(message=_('%(filepath)s is not a regular file') % {'filepath': filepath})
        filesize = stat_result['size']
        TransferRecord().update(record['id'], {'filesize': filesize})
        fileobj = sftp.open(filepath, "rb")
        fileobj.close = _close_proxy(fileobj.close, record)
        return fileobj, filesize


class TransferRecord(resource.TransferRecord):
    def list(self, filters=None, orders=None, offset=None, limit=None, hooks=None):
        assets = Asset().list_query()
        assets_mapping = {}
        for asset in assets:
            assets_mapping[asset['id']] = asset
        refs = super().list(filters=filters, orders=orders, offset=offset, limit=limit, hooks=hooks)
        for ref in refs:
            ref['asset'] = assets_mapping.get(ref['asset_id'], None)
        return refs


class SessionRecord(resource.SessionRecord):
    def list(self, filters=None, orders=None, offset=None, limit=None, hooks=None):
        assets = Asset().list_query()
        assets_mapping = {}
        for asset in assets:
            assets_mapping[asset['id']] = asset
        refs = super().list(filters=filters, orders=orders, offset=offset, limit=limit, hooks=hooks)
        for ref in refs:
            ref['asset'] = assets_mapping.get(ref['asset_id'], None)
        return refs

    def download(self, rid):
        ref = self.get(rid)
        if ref:
            fullpath = os.path.join(CONF.session.record_path, ref['filepath'])
            if not os.path.exists(fullpath):
                raise exceptions.NotFoundError(resource='File of SessionRecord[%s]' % rid)
            return open(fullpath, 'rb'), os.path.getsize(fullpath)
        else:
            raise exceptions.NotFoundError(resource='SessionRecord[%s]' % rid)


class Permission(resource.Permission):
    def list(self, filters=None, orders=None, offset=None, limit=None, hooks=None):
        assets = Asset().list_query()
        assets_mapping = {}
        for asset in assets:
            assets_mapping[asset['id']] = asset
        refs = super().list(filters=filters, orders=orders, offset=offset, limit=limit, hooks=hooks)
        for ref in refs:
            # process assets
            new_assets = []
            for auth_asset in ref['assets']:
                asset_info = assets_mapping.get(auth_asset['asset_id'], None)
                if asset_info:
                    new_assets.append(asset_info)
            ref['assets'] = new_assets
            # process roles
            ref['roles'] = [role['role'] for role in ref['roles']]
        return refs

    def _addtional_create(self, session, resource, created):
        ref_groups = [('assets', 'asset_id', PermissionAsset), ('roles', 'role', PermissionRole)]
        for field, ref_field, resource_type in ref_groups:
            if field in resource:
                refs = resource[field]
                reduce_refs = list(set(refs))
                reduce_refs.sort(key=refs.index)
                # remove asset_id that user are not permited to view
                if ref_field == 'asset_id':
                    reduce_refs = list(set(reduce_refs) & set([asset['id'] for asset in Asset().list_query()]))
                for ref in reduce_refs:
                    new_ref = {}
                    new_ref['permission_id'] = created['id']
                    new_ref[ref_field] = ref
                    resource_type(transaction=session).create(new_ref)

    def _addtional_update(self, session, rid, resource, before_updated, after_updated):
        ref_groups = [('assets', 'asset_id', PermissionAsset), ('roles', 'role', PermissionRole)]
        for field, ref_field, resource_type in ref_groups:
            if field in resource:
                refs = resource[field]
                # remove asset_id that user are not permited to view
                if ref_field == 'asset_id':
                    refs = list(set(refs) & set([asset['id'] for asset in Asset().list_query()]))
                old_refs = [
                    result[ref_field]
                    for result in resource_type(session=session).list(filters={'permission_id': before_updated['id']})
                ]
                create_refs = list(set(refs) - set(old_refs))
                create_refs.sort(key=refs.index)
                delete_refs = set(old_refs) - set(refs)
                if delete_refs:
                    resource_type(transaction=session).delete_all(filters={
                        'permission_id': before_updated['id'],
                        ref_field: {
                            'in': list(delete_refs)
                        }
                    })
                for ref in create_refs:
                    new_ref = {}
                    new_ref['permission_id'] = before_updated['id']
                    new_ref[ref_field] = ref
                    resource_type(transaction=session).create(new_ref)

    def delete(self, rid, filters=None, detail=True):
        with self.transaction() as session:
            PermissionAsset(transaction=session).delete_all({'permission_id': rid})
            PermissionRole(transaction=session).delete_all({'permission_id': rid})


PermissionAsset = resource.PermissionAsset
PermissionRole = resource.PermissionRole
