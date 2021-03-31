# coding=utf-8

from __future__ import absolute_import

from talos.core import config
from talos.core.i18n import _

CONF = config.CONF


class Language(object):
    """中间件，提供动态i18n切换"""
    def process_request(self, req, resp):
        prefer = _.client_prefers(req.get_header('Accept-Language', default=''))
        if prefer:
            _.change(prefer[0])
        else:
            # fallback to first available language
            available_languages = _.available_languages
            if available_languages:
                _.change(available_languages[0])
