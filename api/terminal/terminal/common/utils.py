# coding=utf-8
"""
terminal.common.utils
~~~~~~~~~~~~~~~~~~~~~

本模块提供项目工具库

"""
import base64
import binascii
import contextlib
import functools
import logging
import os.path
import shutil
import tempfile
import time

import requests
from talos.core import config
from talos.core import exceptions as base_ex
from talos.core.i18n import _
from talos.utils import scoped_globals
from terminal.common import exceptions

try:
    HAS_FCNTL = True
    import fcntl
except:
    HAS_FCNTL = False

LOG = logging.getLogger(__name__)
CONF = config.CONF

# register jar,war,apk as zip file
shutil.register_unpack_format('jar', ['.jar'], shutil._UNPACK_FORMATS['zip'][1])
shutil.register_unpack_format('war', ['.war'], shutil._UNPACK_FORMATS['zip'][1])
shutil.register_unpack_format('apk', ['.apk'], shutil._UNPACK_FORMATS['zip'][1])


def unpack_file(filename, unpack_dest):
    shutil.unpack_archive(filename, unpack_dest)


@contextlib.contextmanager
def lock(name, block=True, timeout=5):
    timeout = 1.0 * timeout
    if HAS_FCNTL:
        acquired = False
        filepath = os.path.join(tempfile.gettempdir(), 'artifacts_lock_%s' % name)
        fp = open(filepath, "a+")
        flag = fcntl.LOCK_EX | fcntl.LOCK_NB
        try:
            if not block:
                # non-block yield immediately
                try:
                    fcntl.flock(fp, flag)
                    acquired = True
                except:
                    pass
                yield acquired
            else:
                # block will try until timeout
                time_pass = 0
                while time_pass < timeout:
                    try:
                        fcntl.flock(fp, flag)
                        acquired = True
                        break
                    except:
                        gap = 0.1
                        time.sleep(gap)
                        time_pass += gap
                yield acquired
        finally:
            if acquired:
                fcntl.flock(fp, fcntl.LOCK_UN)
            fp.close()
    else:
        yield False


def json_or_error(func):
    @functools.wraps(func)
    def _json_or_error(url, **kwargs):
        try:
            try:
                return func(url, **kwargs)
            except requests.ConnectionError as e:
                LOG.error('http error: %s %s, reason: %s', func.__name__.upper(), url, str(e))
                raise base_ex.CallBackError(message={
                    'code': 50002,
                    'title': _('Connection Error'),
                    'description': _('Failed to establish a new connection')
                })
            except requests.Timeout as e:
                LOG.error('http error: %s %s, reason: %s', func.__name__.upper(), url, str(e))
                raise base_ex.CallBackError(message={
                    'code': 50004,
                    'title': _('Timeout Error'),
                    'description': _('Server do not respond')
                })
            except requests.HTTPError as e:
                LOG.error('http error: %s %s, reason: %s', func.__name__.upper(), url, str(e))
                code = int(e.response.status_code)
                message = RestfulJson.get_response_json(e.response, default={'code': code})
                if code == 401:
                    raise base_ex.AuthError()
                if code == 404:
                    message['title'] = _('Not Found')
                    message['description'] = _('The resource you request not exist')
                # 如果后台返回的数据不符合要求，强行修正
                if 'code' not in message:
                    message['code'] = code
                if 'title' not in message:
                    message['title'] = message.get('title', e.response.reason)
                if 'description' not in message:
                    message['description'] = message.get('message', str(e))
                raise base_ex.CallBackError(message=message)
            except Exception as e:
                LOG.error('http error: %s %s, reason: %s', func.__name__.upper(), url, str(e))
                message = RestfulJson.get_response_json(e.response,
                                                        default={
                                                            'code': 500,
                                                            'title': _('Server Error'),
                                                            'description': str(e)
                                                        })
                if 'code' not in message:
                    message['code'] = 500
                if 'title' not in message:
                    message['title'] = message.get('title', str(e))
                if 'description' not in message:
                    message['description'] = message.get('message', str(e))
                raise base_ex.CallBackError(message=message)
        except base_ex.CallBackError as e:
            raise exceptions.PluginError(message=e.message, error_code=e.code)

    return _json_or_error


class RestfulJson(object):
    @staticmethod
    def get_response_json(resp, default=None):
        try:
            return resp.json()
        except Exception as e:
            return default

    @staticmethod
    @json_or_error
    def post(url, **kwargs):
        resp = requests.post(url, **kwargs)
        resp.raise_for_status()
        return RestfulJson.get_response_json(resp)

    @staticmethod
    @json_or_error
    def get(url, **kwargs):
        resp = requests.get(url, **kwargs)
        resp.raise_for_status()
        return RestfulJson.get_response_json(resp)

    @staticmethod
    @json_or_error
    def patch(url, **kwargs):
        resp = requests.patch(url, **kwargs)
        resp.raise_for_status()
        return RestfulJson.get_response_json(resp)

    @staticmethod
    @json_or_error
    def delete(url, **kwargs):
        resp = requests.delete(url, **kwargs)
        resp.raise_for_status()
        return RestfulJson.get_response_json(resp)

    @staticmethod
    @json_or_error
    def put(url, **kwargs):
        resp = requests.put(url, **kwargs)
        resp.raise_for_status()
        return RestfulJson.get_response_json(resp)


def b64decode_key(key):
    new_key = key
    max_padding = 3
    while max_padding > 0:
        try:
            return base64.b64decode(new_key)
        except binascii.Error as e:
            new_key += '='
            max_padding -= 1
            if max_padding <= 0:
                raise e


def get_token():
    # TODO: create new token if CONF.wecube.use_token is False
    return scoped_globals.GLOBALS.request.auth_token or CONF.wecube.token


def transform_filter_to_cmdb_query(filters, orders=None, offset=None, limit=None):
    '''transform filter from talos filters to wecmdb filters
    '''
    # TODO: not finish
    pass