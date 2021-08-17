# coding=utf-8

from __future__ import absolute_import
import datetime

from talos.core.i18n import _
from talos.core import config
from talos.db import crud
from talos.core import utils
from talos.db import validator
from talos.utils import scoped_globals

from terminal.common import exceptions
from terminal.common import utils as terminal_utils
from terminal.db import models
from terminal.db import validator as my_validator

CONF = config.CONF


class MetaCRUD(crud.ResourceBase):
    _id_prefix = ''

    def _before_create(self, resource, validate):
        if 'id' not in resource and self._id_prefix:
            resource['id'] = utils.generate_prefix_uuid(self._id_prefix)
        resource['created_by'] = scoped_globals.GLOBALS.request.auth_user or None
        resource['created_time'] = datetime.datetime.now()

    def _before_update(self, rid, resource, validate):
        resource['updated_by'] = scoped_globals.GLOBALS.request.auth_user or None
        resource['updated_time'] = datetime.datetime.now()


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
        crud.ColumnValidator(field='created_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='created_time', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_time', validate_on=('create:O', 'update:O'), nullable=True),
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
        crud.ColumnValidator(field='created_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='created_time', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_time', validate_on=('create:O', 'update:O'), nullable=True)
    ]


class BookmarkRole(crud.ResourceBase):
    orm_meta = models.BookmarkRole
    _default_order = ['-id']


class JumpServer(MetaCRUD):
    orm_meta = models.JumpServer
    _default_order = ['-id']
    _encrypted_fields = ['password']
    _id_prefix = 'server-'

    _validate = [
        crud.ColumnValidator(field='id', validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='name',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='scope',
                             rule=my_validator.ConcatCIDRValidator(),
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
        crud.ColumnValidator(field='created_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='created_time', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_time', validate_on=('create:O', 'update:O'), nullable=True),
    ]

    def _before_create(self, resource, validate):
        super()._before_create(resource, validate)
        for field in self._encrypted_fields:
            if resource.get(field, None) is not None:
                resource[field] = terminal_utils.platform_encrypt(resource[field], resource['id'],
                                                                  CONF.platform_encrypt_seed)

    def _before_update(self, rid, resource, validate):
        super()._before_update(rid, resource, validate)
        for field in self._encrypted_fields:
            if resource.get(field, None) is not None:
                resource[field] = terminal_utils.platform_encrypt(resource[field], rid, CONF.platform_encrypt_seed)

    def list_internal(self, filters=None, orders=None, offset=None, limit=None, hooks=None):
        refs = super().list(filters=filters, orders=orders, offset=offset, limit=limit, hooks=hooks)
        for ref in refs:
            for field in self._encrypted_fields:
                ref[field] = terminal_utils.platform_decrypt(ref[field], ref['id'], CONF.platform_encrypt_seed)
        return refs
