# coding=utf-8

from __future__ import absolute_import

from terminal.common.controller import Collection, Item
from terminal.apps.assets import api as files_api


class CollectionAssets(Collection):
    name = 'terminal.assets'
    resource = files_api.Asset
    allow_methods = ('GET', )

    def on_get(self, req, resp, **kwargs):
        self._validate_method(req)
        refs = []
        count = 0
        criteria = self._build_criteria(req)
        if criteria:
            count, refs = self.list(req, criteria, **kwargs)
            for r in refs:
                # remove password info
                r.pop('password', None)
        resp.json = {'code': 200, 'status': 'OK', 'data': {'count': count, 'data': refs}, 'message': 'success'}


# class ItemAssetFile(Item):
#     name = 'terminal.assets.file'
#     resource = files_api.AssetFile

# class CollectionRecords(Collection):
#     name = 'terminal.records'
#     resource = files_api.Record

# class ItemRecordFile(Item):
#     name = 'terminal.records.file'
#     resource = files_api.RecordFile

# class CollectionRecordCommands(Collection):
#     name = 'terminal.records.commands'
#     resource = files_api.RecordCommand

# class CollectionPermissions(Collection):
#     name = 'terminal.permissions'
#     resource = files_api.Permission

# class ItemPermission(Item):
#     name = 'terminal.permissions'
#     resource = files_api.Permission