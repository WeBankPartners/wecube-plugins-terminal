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

    def _addtional_create(self, session, resource, created):
        ref_groups = [('assets', 'asset_id', PermissionAsset), ('roles', 'role', PermissionRole)]
        for field, ref_field, resource_type in ref_groups:
            if field in resource:
                refs = resource[field]
                reduce_refs = list(set(refs))
                reduce_refs.sort(key=refs.index)
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


class SessionRecord(crud.ResourceBase):
    orm_meta = models.SessionRecord
    _default_order = ['-id']


class TransferRecord(crud.ResourceBase):
    orm_meta = models.TransferRecord
    _default_order = ['-id']
