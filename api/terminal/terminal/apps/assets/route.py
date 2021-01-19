# coding=utf-8

from __future__ import absolute_import

from terminal.apps.assets import controller


def add_routes(api):
    api.add_route('/terminal/v1/assets', controller.CollectionAssets())
    api.add_route('/terminal/v1/assets/{rid}/file', controller.ItemAssetFile())
    # api.add_route('/terminal/v1/records', controller.CollectionRecords())
    # api.add_route('/terminal/v1/records/{rid}/playback', controller.ItemRecordFile())
    # api.add_route('/terminal/v1/records/{rid}/commands', controller.CollectionRecordCommands())
    # api.add_route('/terminal/v1/permissions', controller.CollectionPermissions())
    # api.add_route('/terminal/v1/permissions/{rid}', controller.ItemPermission())
