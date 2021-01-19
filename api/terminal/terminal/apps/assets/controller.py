# coding=utf-8

from __future__ import absolute_import

import os.path
import cgi
from talos.core.i18n import _

from terminal.common import exceptions
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


class ItemAssetFile(Item):
    name = 'terminal.assets.file'
    resource = files_api.AssetFile

    def on_post(self, req, resp, **kwargs):
        path = req.params.get('path', None)
        if not path:
            raise exceptions.ValidationError(message=_('missing query: %(name)s') % {'name': 'path'})
        form = cgi.FieldStorage(fp=req.stream, environ=req.env)
        if 'file' not in form:
            raise exceptions.ValidationError(message=_('form-data named "%(name)s" not found') % {'name': 'file'})
        resp.json = {
            'code': 200,
            'status': 'OK',
            'data': self.upload(req, form['file'].filename, form['file'].file, path, **kwargs),
            'message': 'success'
        }

    def upload(self, req, filename, fileobj, destpath, **kwargs):
        return self.resource().upload(filename, fileobj, destpath, **kwargs)

    def on_get(self, req, resp, **kwargs):
        path = req.params.get('path', None)
        if not path:
            raise exceptions.ValidationError(message=_('missing query: %(name)s') % {'name': 'path'})
        stream, stream_len = self.download(req, path, **kwargs)
        resp.set_stream(stream, stream_len)
        resp.set_header('Content-Disposition',
                        ("attachment;filename=" + os.path.basename(path)).encode('utf8').decode('latin-1'))
        resp.set_header('Content-Type', 'application/octet-stream')

    def download(self, req, filepath, **kwargs):
        return self.resource().download(filepath, **kwargs)


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