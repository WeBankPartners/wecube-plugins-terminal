# coding=utf-8

from __future__ import absolute_import

from terminal.apps.openapi import controller


def add_routes(api):
    api.add_route('/terminal/apispec', controller.Apispec())
    api.add_route('/terminal/redoc', controller.Redoc())
    api.add_route('/terminal/swagger', controller.Swagger())
