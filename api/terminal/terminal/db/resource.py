# coding=utf-8

from __future__ import absolute_import
import datetime

from talos.core.i18n import _
from talos.db import crud
from talos.db import validator
from talos.utils import scoped_globals

from terminal.common import exceptions
from terminal.db import models
from terminal.db import validator as my_validator


class MetaCRUD(crud.ResourceBase):
    def _before_create(self, resource, validate):
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
