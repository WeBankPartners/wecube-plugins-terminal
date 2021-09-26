# coding=utf-8

from __future__ import absolute_import

import datetime
import logging
import os.path
import re

import ipaddress
from talos.common import cache
from talos.core import config
from talos.core.i18n import _
from talos.utils.scoped_globals import GLOBALS
from terminal.db import resource
from terminal.common import wecmdb
from terminal.common import wecube
from terminal.common import expression
from terminal.common import ssh
from terminal.common import utils
from terminal.common import exceptions
from terminal.common import s3

CONF = config.CONF
LOG = logging.getLogger(__name__)
TOKEN_KEY = 'terminal_subsystem_token'


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

    def get_connection_info(self, rid, auth_roles=None, auth_type='execute'):
        datas = self.list({'id': rid}, auth_roles=auth_roles, auth_type=auth_type)
        if not datas:
            raise exceptions.PluginError(message=_('Not allowed to perform %(action)s on Asset(#%(id)s)') % {
                'id': rid,
                'action': auth_type
            })
        asset = datas[0]
        if isinstance(asset['port'], str) and asset['port'].isnumeric():
            asset['port'] = int(asset['port']) or 22
        elif isinstance(asset['port'], int):
            pass
        else:
            asset['port'] = 22
        return asset

    def list_query(self, filters=None, orders=None, offset=None, limit=None, hooks=None):
        if CONF.server.mode == 'standalone':
            return AssetMgmt().list(filters=filters, orders=orders, offset=offset, limit=limit)
        else:
            cached_key = 'terminal.asset.list_query/' + str(filters)
            datas = cache.get(cached_key, 5)
            if cache.validate(datas):
                return datas
            fields = {
                'id': 'id',
                CONF.asset.asset_field_name: 'name',
                'displayName': 'display_name',
                CONF.asset.asset_field_ip: 'ip_address',
                CONF.asset.asset_field_port: 'port',
                CONF.asset.asset_field_user: 'username',
                CONF.asset.asset_field_desc: 'description'
            }
            client = wecmdb.EntityClient(CONF.wecube.base_url, self._token)
            filters = filters or {}
            # expression search
            filter_expression = filters.pop('expression', None)
            query = utils.transform_filter_to_entity_query(filters, fields_mapping=fields)
            package, entity = CONF.asset.asset_type.split(':')
            resp_json = client.retrieve(package, entity, query)
            datas = resp_json.get('data', [])
            datas = self._transform_field(datas, fields)
            if filter_expression:
                # validate expression
                if not isinstance(filter_expression, str):
                    raise exceptions.ValidationError(
                        message=_('%(expression)s not acceptable, expect url?expression=value') %
                        {'expression': filter_expression})
                query_expression_groups = []
                try:
                    query_expression_groups = expression.expr_parse(filter_expression)
                except exceptions.PluginError as e:
                    LOG.exception(e)
                if not query_expression_groups:
                    raise exceptions.ValidationError(message=_('%(expression)s invalid') %
                                                     {'expression': filter_expression})
                # if last expr_group is not CONF.asset.asset_type, return empty list
                if '%s:%s' % (query_expression_groups[-1].get('data', {}).get('plugin', ''),
                              query_expression_groups[-1].get('data', {}).get('ci', '')) == CONF.asset.asset_type:
                    wecube_client = wecube.WeCubeClient(CONF.wecube.base_url, None)
                    subsys_token = cache.get_or_create(TOKEN_KEY, wecube_client.login_subsystem, expires=600)
                    wecube_client.token = subsys_token
                    expression_assets = wecube_client.post(
                        wecube_client.build_url('/platform/v1/data-model/dme/integrated-query'), {
                            'dataModelExpression': filter_expression,
                            'filters': []
                        })
                    expression_assets = expression_assets['data'] or []
                    expression_assets_ids = set([item['id'] for item in expression_assets])
                    datas = [item for item in datas if item['id'] in expression_assets_ids]
                else:
                    datas = []
            cache.set(cached_key, datas)
            return datas

    def list(self,
             filters=None,
             orders=None,
             offset=None,
             limit=None,
             hooks=None,
             auth_roles=None,
             auth_type='execute'):
        permission_filters = {"roles.role": {'in': auth_roles or list(GLOBALS.request.auth_permissions)}, 'enabled': 1}
        permission_filters['auth_' + auth_type] = 1
        permissions = resource.Permission().list(permission_filters)
        auth_asset_ids = []
        if CONF.server.mode == 'standalone':
            for permission in permissions:
                auth_asset_ids.extend([auth_asset['asset_id'] for auth_asset in permission['assets']])
            auth_asset_ids = set(auth_asset_ids)
            if auth_asset_ids:
                assets = AssetMgmt().list_internal(filters=filters)
                for item in assets:
                    item['connnection_url'] = CONF.websocket_url
                assets = [item for item in assets if item['id'] in auth_asset_ids]
                return assets
        else:
            fields = {
                'id': 'id',
                CONF.asset.asset_field_name: 'name',
                'displayName': 'display_name',
                CONF.asset.asset_field_ip: 'ip_address',
                CONF.asset.asset_field_port: 'port',
                CONF.asset.asset_field_user: 'username',
                CONF.asset.asset_field_password: 'password',
                CONF.asset.asset_field_desc: 'description'
            }
            for permission in permissions:
                expression_assets = self.list_asset_by_expression(permission['expression'], fields)
                auth_asset_ids.extend([auth_asset['asset_id'] for auth_asset in permission['assets']])
                auth_asset_ids.extend([asset['id'] for asset in expression_assets])
            auth_asset_ids = set(auth_asset_ids)

            datas = []
            filters = filters or {}
            # expression search
            filter_expression = filters.pop('expression', None)
            if auth_asset_ids:
                filters.setdefault('id', {'in': list(auth_asset_ids)})
                client = wecmdb.EntityClient(CONF.wecube.base_url, self._token)
                query = utils.transform_filter_to_entity_query(filters, fields_mapping=fields)
                package, entity = CONF.asset.asset_type.split(':')
                resp_json = client.retrieve(package, entity, query)
                datas = resp_json.get('data', [])
                datas = self._transform_field(datas, fields)
                if filter_expression:
                    # validate expression
                    if not isinstance(filter_expression, str):
                        raise exceptions.ValidationError(
                            message=_('%(expression)s not acceptable, expect url?expression=value') %
                            {'expression': filter_expression})
                    query_expression_groups = []
                    try:
                        query_expression_groups = expression.expr_parse(filter_expression)
                    except exceptions.PluginError as e:
                        LOG.exception(e)
                    if not query_expression_groups:
                        raise exceptions.ValidationError(message=_('%(expression)s invalid') %
                                                         {'expression': filter_expression})
                    # if last expr_group is not CONF.asset.asset_type, return empty list
                    if '%s:%s' % (query_expression_groups[-1].get('data', {}).get('plugin', ''),
                                  query_expression_groups[-1].get('data', {}).get('ci', '')) == CONF.asset.asset_type:
                        wecube_client = wecube.WeCubeClient(CONF.wecube.base_url, None)
                        subsys_token = cache.get_or_create(TOKEN_KEY, wecube_client.login_subsystem, expires=600)
                        wecube_client.token = subsys_token
                        expression_assets = wecube_client.post(
                            wecube_client.build_url('/platform/v1/data-model/dme/integrated-query'), {
                                'dataModelExpression': filter_expression,
                                'filters': []
                            })
                        expression_assets = expression_assets['data'] or []
                        expression_assets_ids = set([item['id'] for item in expression_assets])
                        datas = [item for item in datas if item['id'] in expression_assets_ids]
                    else:
                        datas = []

            datas = [item for item in datas if item['id'] in auth_asset_ids]
            for item in datas:
                item['connnection_url'] = CONF.websocket_url
                # decrypt password if encrypted
                encrypted_prefix = '{cipher_a}'
                if item['password'].startswith(encrypted_prefix):
                    origin_password = item['password'][len(encrypted_prefix):]
                    origin_password = bytes.fromhex(origin_password)
                    key = utils.md5(item['id'] + CONF.platform_encrypt_seed)[:16]
                    origin_password = utils.aes_cbc_pkcs7_decrypt(origin_password, key, key)
                    item['password'] = origin_password.decode()
            return datas
        return []

    def list_asset_by_expression(self, expression, field_mapping):
        if expression:
            wecube_client = wecube.WeCubeClient(CONF.wecube.base_url, None)
            wecube_client.token = self._token
            resp = wecube_client.post(wecube_client.build_url('/platform/v1/data-model/dme/integrated-query'), {
                'dataModelExpression': expression,
                'filters': []
            })
            assets = resp['data'] or []
            return self._transform_field(assets, field_mapping)
        return []


class AssetFile(object):
    def upload(self, filename, fileobj, destpath, rid):
        asset = Asset().get_connection_info(rid, auth_type='upload')
        fullpath = os.path.join(destpath, filename)
        client = ssh.SSHClient()
        jump_servers = JumpServer().get_jump_servers(asset['ip_address'])
        client.connect(asset['ip_address'],
                       asset['username'],
                       asset['password'],
                       port=asset['port'],
                       jump_servers=jump_servers)
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
            TransferRecord().update(record['id'], {
                'ended_time': datetime.datetime.now(),
                'status': 'ERROR',
                'message': 'File not found'
            })
            raise exceptions.ValidationError(message=_('%(filepath)s not exist') % {'filepath': destpath})
        except PermissionError:
            TransferRecord().update(record['id'], {
                'ended_time': datetime.datetime.now(),
                'status': 'ERROR',
                'message': 'Permission denied'
            })
            raise exceptions.ValidationError(message=_('upload to %(filepath)s error: permission denied') %
                                             {'filepath': destpath})
        return fullpath

    def download(self, filepath, rid):
        # closeable wrapper
        def _close_proxy(func, record):
            def ___close_proxy(*args, **kwargs):
                TransferRecord().update(record['id'], {'ended_time': datetime.datetime.now(), 'status': 'OK'})
                return func(*args, **kwargs)

            return ___close_proxy

        asset = Asset().get_connection_info(rid, auth_type='download')
        client = ssh.SSHClient()
        jump_servers = JumpServer().get_jump_servers(asset['ip_address'])
        client.connect(asset['ip_address'],
                       asset['username'],
                       asset['password'],
                       port=asset['port'],
                       jump_servers=jump_servers)
        sftp = client.create_sftp()
        record = TransferRecord().create({
            'asset_id': rid,
            'filepath': filepath,
            'filesize': 0,
            'user': GLOBALS.request.auth_user,
            'operation_type': 'download',
            'started_time': datetime.datetime.now()
        })
        try:
            stat_result = sftp.stat(filepath)
        except FileNotFoundError as e:
            TransferRecord().update(record['id'], {
                'ended_time': datetime.datetime.now(),
                'status': 'ERROR',
                'message': 'File not found'
            })
            raise exceptions.ValidationError(message=_('%(filepath)s not exist') % {'filepath': filepath})
        except PermissionError:
            TransferRecord().update(record['id'], {
                'ended_time': datetime.datetime.now(),
                'status': 'ERROR',
                'message': 'Permission denied'
            })
            raise exceptions.ValidationError(message=_('download %(filepath)s error: permission denied') %
                                             {'filepath': filepath})
        stat_result = ssh.SSHClient.format_sftp_attr('./', stat_result)
        if stat_result['type'] != ssh.FileType.T_FILE:
            TransferRecord().update(record['id'], {
                'ended_time': datetime.datetime.now(),
                'status': 'ERROR',
                'message': 'Not regular file'
            })
            raise exceptions.ValidationError(message=_('%(filepath)s is not a regular file') % {'filepath': filepath})
        filesize = stat_result['size']
        if filesize and filesize > int(CONF.download_max_size):
            TransferRecord().update(
                record['id'], {
                    'ended_time': datetime.datetime.now(),
                    'status': 'ERROR',
                    'message': 'File size (%s bytes) exceeds maximum of %s' % (filesize, CONF.download_max_size)
                })
            raise exceptions.ValidationError(
                message=_('file size (%(size)s bytes) exceeds maximum of %(maximum_size)s') % {
                    'size': filesize,
                    'maximum_size': CONF.download_max_size
                })
        TransferRecord().update(record['id'], {'filesize': filesize})
        fileobj = sftp.open(filepath, "rb")
        fileobj.close = _close_proxy(fileobj.close, record)
        return fileobj, filesize


class AssetPermission(object):
    def permission(self, auth_roles, rid):
        permission_filters = {
            "roles.role": {
                'in': auth_roles or list(GLOBALS.request.auth_permissions)
            },
            "assets.asset_id": rid,
            'enabled': 1
        }
        auth_permissions = Permission().list(permission_filters)
        results = set()
        permissions = ['upload', 'download', 'execute']
        for auth_permission in auth_permissions:
            for permission in permissions:
                if auth_permission.get('auth_' + permission, False):
                    results.add(permission)
        return list(results)


class TransferRecord(resource.TransferRecord):
    def list(self, filters=None, orders=None, offset=None, limit=None, hooks=None):
        refs = super().list(filters=filters, orders=orders, offset=offset, limit=limit, hooks=hooks)
        assets = []
        assets_mapping = {}
        query_asset_ids = list(set([r['asset_id'] for r in refs]))
        if query_asset_ids:
            assets = Asset().list_query(filters={'id': {'in': query_asset_ids}})
        for asset in assets:
            assets_mapping[asset['id']] = asset
        for ref in refs:
            ref['asset'] = assets_mapping.get(ref['asset_id'], None)
        return refs


class SessionRecord(resource.SessionRecord):
    def list(self, filters=None, orders=None, offset=None, limit=None, hooks=None):
        refs = super().list(filters=filters, orders=orders, offset=offset, limit=limit, hooks=hooks)
        assets = []
        assets_mapping = {}
        query_asset_ids = list(set([r['asset_id'] for r in refs]))
        if query_asset_ids:
            assets = Asset().list_query(filters={'id': {'in': query_asset_ids}})
        for asset in assets:
            assets_mapping[asset['id']] = asset
        for ref in refs:
            ref['asset'] = assets_mapping.get(ref['asset_id'], None)
        return refs

    def download(self, rid):
        ref = self.get(rid)
        if ref:
            if CONF.s3.server and CONF.s3.server in ref['filepath']:
                client = s3.S3Client(CONF.s3.server, CONF.s3.access_key, CONF.s3.secret_key)
                return client.download_stream(ref['filepath'])
            else:
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
            return super().delete(rid, filters, detail)


PermissionAsset = resource.PermissionAsset
PermissionRole = resource.PermissionRole


class Bookmark(resource.Bookmark):
    def count(self, filters=None, offset=None, limit=None, hooks=None):
        auth_roles = GLOBALS.request.auth_permissions
        filters = filters or {}
        filters['roles.role'] = {'in': list(auth_roles)}
        return super().count(filters=filters, offset=offset, limit=limit, hooks=hooks)

    def list(self, filters=None, orders=None, offset=None, limit=None, hooks=None):
        auth_roles = GLOBALS.request.auth_permissions
        filters = filters or {}
        filters['roles.role'] = {'in': list(auth_roles)}
        refs = super().list(filters=filters, orders=orders, offset=offset, limit=limit, hooks=hooks)
        for ref in refs:
            # process roles
            role_mapping = {'owner': [], 'executor': []}
            for role in ref['roles']:
                role_mapping[role['type']].append(role['role'])
            if set(role_mapping['owner']) & auth_roles:
                ref['is_owner'] = 1
            else:
                ref['is_owner'] = 0
            ref['roles'] = role_mapping
        return refs

    def _addtional_create(self, session, data, created):
        if 'roles' in data:
            refs = data['roles']
            role_owner = refs.get('owner', []) or []
            role_executor = refs.get('executor', []) or []
            ref_groups = [(role_owner, 'owner', resource.BookmarkRole),
                          (role_executor, 'executor', resource.BookmarkRole)]
            for role_refs, ref_type, resource_type in ref_groups:
                reduce_refs = list(set(role_refs))
                reduce_refs.sort(key=role_refs.index)
                if ref_type == 'owner' and len(reduce_refs) == 0:
                    raise exceptions.ValidationError(message=_('length of roles.owner must be >= 1'))
                for ref in reduce_refs:
                    new_ref = {}
                    new_ref['bookmark_id'] = created['id']
                    new_ref['role'] = ref
                    new_ref['type'] = ref_type
                    resource_type(transaction=session).create(new_ref)

    def _addtional_update(self, session, rid, data, before_updated, after_updated):
        if 'roles' in data:
            refs = data['roles']
            role_owner = refs.get('owner', None)
            role_executor = refs.get('executor', None)
            ref_groups = [(role_owner, 'owner', resource.BookmarkRole),
                          (role_executor, 'executor', resource.BookmarkRole)]
            for role_refs, ref_type, resource_type in ref_groups:
                if role_refs is None:
                    continue
                reduce_refs = list(set(role_refs))
                reduce_refs.sort(key=role_refs.index)
                if ref_type == 'owner' and len(reduce_refs) == 0:
                    raise exceptions.ValidationError(message=_('length of roles.owner must be >= 1'))
                old_refs = [
                    result['role'] for result in resource_type(session=session).list(filters={
                        'bookmark_id': before_updated['id'],
                        'type': ref_type
                    })
                ]
                create_refs = list(set(reduce_refs) - set(old_refs))
                create_refs.sort(key=reduce_refs.index)
                delete_refs = set(old_refs) - set(reduce_refs)

                if delete_refs:
                    resource_type(transaction=session).delete_all(filters={
                        'bookmark_id': before_updated['id'],
                        'type': ref_type
                    })
                for ref in create_refs:
                    new_ref = {}
                    new_ref['bookmark_id'] = before_updated['id']
                    new_ref['role'] = ref
                    new_ref['type'] = ref_type
                    resource_type(transaction=session).create(new_ref)

    def update(self, rid, data, filters=None, validate=True, detail=True):
        auth_roles = GLOBALS.request.auth_permissions
        if super().count({'id': rid}) and resource.BookmarkRole().count({
                'bookmark_id': rid,
                'role': {
                    'in': list(auth_roles)
                },
                'type': 'owner'
        }) == 0:
            raise exceptions.ValidationError(message=_('the resource(%(resource)s) does not belong to you') %
                                             {'resource': 'Bookmark[%s]' % rid})
        return super().update(rid, data, filters=filters, validate=validate, detail=detail)

    def delete(self, rid, filters=None, detail=True):
        auth_roles = GLOBALS.request.auth_permissions
        if super().count({'id': rid}) and resource.BookmarkRole().count({
                'bookmark_id': rid,
                'role': {
                    'in': list(auth_roles)
                },
                'type': 'owner'
        }) == 0:
            raise exceptions.ValidationError(message=_('the resource(%(resource)s) does not belong to you') %
                                             {'resource': 'Bookmark[%s]' % rid})
        return super().delete(rid, filters=filters, detail=detail)


class JumpServer(resource.JumpServer):
    def get_jump_servers(self, dst_ip):
        def is_belong(cidr, ip):
            try:
                cidr_network = ipaddress.IPv4Network(cidr)
                return ip in cidr_network
            except Exception:
                return False

        try:
            dst_ip = ipaddress.IPv4Address(dst_ip)
        except Exception:
            return None

        rets = []
        servers = self.list_internal()
        splitter = r',|\||;'
        for server in servers:
            cidrs = re.split(splitter, server['scope'] or '')
            cidrs = [x for x in cidrs if x]
            for cidr in cidrs:
                if is_belong(cidr, dst_ip):
                    rets.append((server['ip_address'], server['port'], server['username'], server['password']))
        return rets


class AssetMgmt(resource.Asset):
    pass
