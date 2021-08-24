# coding=utf-8

from __future__ import absolute_import

from terminal.apps.assets import controller


def add_routes(api):
    api.add_route('/terminal/v1/assets', controller.CollectionAssets())
    api.add_route('/terminal/v1/view-assets', controller.CollectionViewAssets())
    api.add_route('/terminal/v1/assets/{rid}/file', controller.ItemAssetFile())
    api.add_route('/terminal/v1/assets/{rid}/permissions', controller.ItemAssetPermission())
    api.add_route('/terminal/v1/transfer-records', controller.CollectionTransferRecords())
    api.add_route('/terminal/v1/session-records', controller.CollectionSessionRecords())
    api.add_route('/terminal/v1/session-records/{rid}/file', controller.ItemSessionRecordFile())
    api.add_route('/terminal/v1/permissions', controller.CollectionPermissions())
    api.add_route('/terminal/v1/permissions/{rid}', controller.ItemPermission())
    api.add_route('/terminal/v1/bookmarks', controller.CollectionBookmarks())
    api.add_route('/terminal/v1/bookmarks/{rid}', controller.ItemBookmark())
    api.add_route('/terminal/v1/jumpservers', controller.CollectionJumpServers())
    api.add_route('/terminal/v1/jumpservers/{rid}', controller.ItemJumpServer())
    api.add_route('/terminal/v1/mgmt-assets', controller.CollectionAssetMgmt())
    api.add_route('/terminal/v1/mgmt-assets/{rid}', controller.ItemAssetMgmt())
