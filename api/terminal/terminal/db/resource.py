# coding=utf-8

from __future__ import absolute_import

import datetime

from talos.core import config, utils
from talos.db import crud, validator
from talos.utils import scoped_globals

from terminal.common import utils as terminal_utils
from terminal.db import models
from terminal.db import validator as my_validator

CONF = config.CONF


class MetaCRUD(crud.ResourceBase):
    _id_prefix = ''
    _remove_fields = []
    _encrypted_fields = []

    def _before_create(self, resource, validate):
        if 'id' not in resource and self._id_prefix:
            resource['id'] = utils.generate_prefix_uuid(self._id_prefix)
        resource['created_by'] = scoped_globals.GLOBALS.request.auth_user or None
        resource['created_time'] = datetime.datetime.now()
        for field in self._encrypted_fields:
            if resource.get(field, None) is not None:
                resource[field] = terminal_utils.platform_encrypt(resource[field], resource['id'],
                                                                  CONF.platform_encrypt_seed)

    def _before_update(self, rid, resource, validate):
        resource['updated_by'] = scoped_globals.GLOBALS.request.auth_user or None
        resource['updated_time'] = datetime.datetime.now()
        for field in self._encrypted_fields:
            if resource.get(field, None) is not None:
                resource[field] = terminal_utils.platform_encrypt(resource[field], rid, CONF.platform_encrypt_seed)

    def create(self, resource, validate=True, detail=True):
        ref = super().create(resource, validate=validate, detail=detail)
        if ref and self._remove_fields:
            for field in self._remove_fields:
                del ref[field]
        return ref

    def list(self, filters=None, orders=None, offset=None, limit=None, hooks=None):
        refs = super().list(filters=filters, orders=orders, offset=offset, limit=limit, hooks=hooks)
        if self._remove_fields:
            for ref in refs:
                for field in self._remove_fields:
                    del ref[field]
        return refs

    def get(self, rid):
        ref = super().get(rid)
        if ref and self._remove_fields:
            for field in self._remove_fields:
                del ref[field]
        return ref

    def update(self, rid, resource, filters=None, validate=True, detail=True):
        before_update, after_update = super().update(rid, resource, filters=filters, validate=validate, detail=detail)
        if before_update and self._remove_fields:
            for field in self._remove_fields:
                del before_update[field]
        if after_update and self._remove_fields:
            for field in self._remove_fields:
                del after_update[field]
        return (before_update, after_update)

    def delete(self, rid, filters=None, detail=True):
        num_ref, refs = super().delete(rid, filters=filters, detail=detail)
        for ref in refs:
            if self._remove_fields:
                for field in self._remove_fields:
                    del ref[field]
        return (num_ref, refs)

    def delete_all(self, filters=None):
        num_ref, refs = super().delete_all(filters=filters)
        for ref in refs:
            if self._remove_fields:
                for field in self._remove_fields:
                    del ref[field]
        return (num_ref, refs)


class PermissionAsset(crud.ResourceBase):
    orm_meta = models.PermissionAsset


class PermissionRole(crud.ResourceBase):
    orm_meta = models.PermissionRole


class Permission(MetaCRUD):
    orm_meta = models.Permission
    _default_order = ['-id']
    _validate = [
        crud.ColumnValidator(field='name',
                             rule=my_validator.LengthValidator(1, 36),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='description',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='auth_upload', rule_type='in', rule=[0, 1], validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='auth_download', rule_type='in', rule=[0, 1], validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='auth_execute', rule_type='in', rule=[0, 1], validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='expression',
                             rule=my_validator.LengthValidator(0, 10240),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='enabled', rule_type='in', rule=[0, 1], validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='created_by', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='created_time', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='updated_by', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='updated_time', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='assets',
                             rule=validator.TypeValidator(list),
                             validate_on=('create:O', 'update:O'),
                             orm_required=False),
        crud.ColumnValidator(field='roles',
                             rule=validator.TypeValidator(list),
                             validate_on=('create:O', 'update:O'),
                             orm_required=False)
    ]


class SessionRecord(crud.ResourceBase):
    orm_meta = models.SessionRecord
    _default_order = ['-id']


class TransferRecord(crud.ResourceBase):
    orm_meta = models.TransferRecord
    _default_order = ['-id']


class Bookmark(MetaCRUD):
    orm_meta = models.Bookmark
    _default_order = ['-id']

    _validate = [
        crud.ColumnValidator(field='name',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='512',
                             rule=my_validator.LengthValidator(0, 512),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='expression',
                             rule=my_validator.LengthValidator(1, 512),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='created_by', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='created_time', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='updated_by', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='updated_time', validate_on=('*:O', ), nullable=True),
    ]


class BookmarkRole(crud.ResourceBase):
    orm_meta = models.BookmarkRole
    _default_order = ['-id']


class JumpServer(MetaCRUD):
    orm_meta = models.JumpServer
    _default_order = ['-created_time']
    _encrypted_fields = ['password']
    _remove_fields = ['password']
    _id_prefix = 'jserver-'

    _validate = [
        crud.ColumnValidator(field='id', validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='name',
                             rule=my_validator.LengthValidator(1, 63),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='scope',
                             rule=my_validator.ConcatCIDRValidator(),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='ip_address',
                             rule=my_validator.validator.Ipv4Validator(),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='port',
                             rule=my_validator.validator.NumberValidator(int, range_min=1, range_max=65535),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='username',
                             rule=my_validator.LengthValidator(1, 36),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='password',
                             rule=my_validator.LengthValidator(1, 255),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='created_by', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='created_time', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='updated_by', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='updated_time', validate_on=('*:O', ), nullable=True),
    ]

    def list_internal(self, filters=None, orders=None, offset=None, limit=None, hooks=None):
        refs = super(MetaCRUD, self).list(filters=filters, orders=orders, offset=offset, limit=limit, hooks=hooks)
        for ref in refs:
            for field in self._encrypted_fields:
                ref[field] = terminal_utils.platform_decrypt(ref[field], ref['id'], CONF.platform_encrypt_seed)
        return refs


class Asset(MetaCRUD):
    orm_meta = models.Asset
    _default_order = ['-created_time']
    _encrypted_fields = ['password']
    _remove_fields = ['password']
    _id_prefix = 'asset-'

    _validate = [
        crud.ColumnValidator(field='id', validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='name',
                             rule=my_validator.LengthValidator(1, 63),
                             validate_on=('create:O', 'update:O')),
        crud.ColumnValidator(field='display_name',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='description',
                             rule=my_validator.LengthValidator(0, 255),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='ip_address',
                             rule=my_validator.validator.Ipv4Validator(),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='port',
                             rule=my_validator.validator.NumberValidator(int, range_min=1, range_max=65535),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='username',
                             rule=my_validator.LengthValidator(1, 36),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='password',
                             rule=my_validator.LengthValidator(1, 255),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='created_by', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='created_time', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='updated_by', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='updated_time', validate_on=('*:O', ), nullable=True),
    ]

    def list_origin(self, filters=None, orders=None, offset=None, limit=None, hooks=None):
        return super(MetaCRUD, self).list(filters=filters, orders=orders, offset=offset, limit=limit, hooks=hooks)

    def list_internal(self, filters=None, orders=None, offset=None, limit=None, hooks=None):
        refs = super(MetaCRUD, self).list(filters=filters, orders=orders, offset=offset, limit=limit, hooks=hooks)
        for ref in refs:
            for field in self._encrypted_fields:
                ref[field] = terminal_utils.platform_decrypt(ref[field], ref['id'], CONF.platform_encrypt_seed)
        return refs


class SysRoleMenu(MetaCRUD):
    orm_meta = models.SysRoleMenu
    _default_order = ['-created_time']


class SysRoleUser(MetaCRUD):
    orm_meta = models.SysRoleUser
    _default_order = ['-created_time']


class SysMenu(MetaCRUD):
    orm_meta = models.SysMenu
    _default_order = ['seq_no']
    _id_prefix = 'menu-'

    _validate = [
        crud.ColumnValidator(field='id', validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='display_name',
                             rule=my_validator.LengthValidator(1, 64),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='url',
                             rule=my_validator.LengthValidator(0, 255),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='seq_no',
                             rule=my_validator.validator.NumberValidator(int, range_min=0, range_max=65535),
                             validate_on=('create:O', 'update:O')),
        crud.ColumnValidator(field='parent',
                             rule=my_validator.BackRefValidator(SysRoleMenu),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='is_active',
                             rule=my_validator.validator.InValidator(['yes', 'no']),
                             validate_on=('create:O', 'update:O')),
        crud.ColumnValidator(field='created_by', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='created_time', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='updated_by', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='updated_time', validate_on=('*:O', ), nullable=True),
    ]


class SysRole(MetaCRUD):
    orm_meta = models.SysRole
    _default_order = ['-created_time']
    _id_prefix = 'role-'
    _detail_relationship_as_summary = True

    _validate = [
        crud.ColumnValidator(field='id', validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='description',
                             rule=my_validator.LengthValidator(1, 255),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='role_type',
                             rule=my_validator.LengthValidator(0, 32),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='is_system',
                             rule=my_validator.validator.InValidator(['yes', 'no']),
                             validate_on=('create:O', 'update:O')),
        crud.ColumnValidator(field='created_by', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='created_time', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='updated_by', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='updated_time', validate_on=('*:O', ), nullable=True),
    ]


class SysUser(MetaCRUD):
    orm_meta = models.SysUser
    _default_order = ['-created_time']
    _remove_fields = ['password', 'salt']
    _id_prefix = 'user-'

    _validate = [
        crud.ColumnValidator(field='id', validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='display_name',
                             rule=my_validator.LengthValidator(1, 64),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='password', rule=my_validator.LengthValidator(1, 128), validate_on=('create:M', )),
        crud.ColumnValidator(field='salt', rule=my_validator.LengthValidator(1, 36), validate_on=('create:M', )),
        crud.ColumnValidator(field='description',
                             rule=my_validator.LengthValidator(0, 255),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='is_system',
                             rule=my_validator.validator.InValidator(['yes', 'no']),
                             validate_on=('create:O', 'update:O')),
        crud.ColumnValidator(field='created_by', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='created_time', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='updated_by', validate_on=('*:O', ), nullable=True),
        crud.ColumnValidator(field='updated_time', validate_on=('*:O', ), nullable=True),
    ]

    def list_internal(self, filters=None, orders=None, offset=None, limit=None, hooks=None):
        return super(MetaCRUD, self).list(filters=filters, orders=orders, offset=offset, limit=limit, hooks=hooks)
