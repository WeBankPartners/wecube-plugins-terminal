# coding=utf-8

from __future__ import absolute_import

import logging
import datetime
from talos.core import config
from talos.core import utils as base_utils
from talos.core import exceptions as base_ex
from terminal.apps.auth import api as auth_api

LOG = logging.getLogger(__name__)
CONF = config.CONF


class Permission(object):
    """中间件，提供API权限校验"""
    def process_resource(self, req, resp, resource, params):
        self._request_started = datetime.datetime.now()
        request_data = getattr(req, 'json', None)
        LOG.info('request  [%s] "%s %s" %s', req.auth_user, req.method, req.relative_uri, request_data)
        controller_name = getattr(resource, 'name', None)
        if controller_name and controller_name in CONF.permission_passthrough:
            return
        if CONF.server.mode == 'standalone':
            user_menus = auth_api.SysUser().get_menus(req.auth_user)
            auth_menu_ids = set([menu['id'] for menu in user_menus])
            menu_ids = set()
            for menu in CONF.menu_permissions:
                if controller_name in CONF.menu_permissions[menu]:
                    menu_ids.add(menu)
            if len(menu_ids & auth_menu_ids) == 0:
                raise base_ex.ForbiddenError()
        else:
            data_permissions = base_utils.get_config(CONF, 'data_permissions', {})
            if controller_name is not None and controller_name in data_permissions:
                permissions = data_permissions[controller_name]
                if isinstance(permissions, dict):
                    permissions = permissions.get(req.method.upper(), []) or []
                if not set(permissions) & req.auth_permissions:
                    raise base_ex.ForbiddenError()
            plugin_permissions = base_utils.get_config(CONF, 'plugin_permissions', [])
            if controller_name is not None and controller_name in plugin_permissions:
                # plugin controller not allow USER access
                if not (req.auth_user == 'SYS_PLATFORM' and 'SUB_SYSTEM' in req.auth_permissions):
                    raise base_ex.ForbiddenError()

    def process_response(self, req, resp, resource, req_succeeded, **kwargs):
        if req_succeeded:
            response_data = getattr(resp, 'json', None)
            request_ended = datetime.datetime.now()
            request_started = getattr(self, '_request_started', None)
            if request_started:
                timepass = request_ended - request_started
                LOG.debug('response [%s] "%s %s" %s %s', req.auth_user, req.method, req.relative_uri, response_data,
                          str(timepass))
