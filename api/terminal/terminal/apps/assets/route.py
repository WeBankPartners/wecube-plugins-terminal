# coding=utf-8

from __future__ import absolute_import

from talos.core.config import CONF
from terminal.apps.assets import controller


def add_routes(api):
    api.add_static_route('/', CONF.ui, fallback_filename='index.html')
    api.add_static_route('/terminal', CONF.ui)
    api.add_static_route('/terminal/css', CONF.ui + '/css')
    api.add_static_route('/terminal/fonts', CONF.ui + '/fonts')
    api.add_static_route('/terminal/img', CONF.ui + '/img')
    api.add_static_route('/terminal/js', CONF.ui + '/js')
    api.add_static_route('/terminal/xtem-player', CONF.ui + '/xtem-player')
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
