# coding=utf-8

from __future__ import absolute_import

import logging
import re
import os
import urllib3
import certifi

import minio
from talos.core.i18n import _
from terminal.common import exceptions

LOG = logging.getLogger(__name__)

R_S3_ENDPOINT = re.compile(
    r'((?P<schema>http|https|s3)://)?(?P<host>[._-a-zA-Z0-9]+(:(\d+))?)(/(?P<bucket>.+?)/(?P<object_key>.+))?')


class S3Client(object):
    def __init__(self, endpoint, access_key, secret_key):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key

    @staticmethod
    def parse_url(url):
        result = {}
        matched = R_S3_ENDPOINT.match(url)
        if matched:
            ref = matched.groupdict()
            result['schema'] = (ref['schema'] or 'http').lower()
            result['secure'] = True if result['schema'] == 'https' else False
            result['host'] = ref['host']
            result['bucket'] = ref['bucket']
            result['object_key'] = ref['object_key']
            return result
        else:
            raise ValueError(_('invalid s3 endpoint url, eg: [(http|https|s3)://]host[:port][/bucket/object_key]'))

    def upload_file(self, bucket, object_key, filepath):
        endpoint_info = self.parse_url(self.endpoint)
        client = minio.Minio(endpoint_info['host'], self.access_key, self.secret_key, secure=endpoint_info['secure'])
        return client.fput_object(bucket, object_key, filepath)

    def download_file(self, url, filepath):
        endpoint_info = self.parse_url(url)
        ca_certs = os.environ.get('SSL_CERT_FILE') or certifi.where()
        http_client = urllib3.PoolManager(timeout=3,
                                          maxsize=10,
                                          cert_reqs='CERT_REQUIRED',
                                          ca_certs=ca_certs,
                                          retries=urllib3.Retry(total=3,
                                                                backoff_factor=0.2,
                                                                status_forcelist=[500, 502, 503, 504]))
        client = minio.Minio(endpoint_info['host'],
                             self.access_key,
                             self.secret_key,
                             secure=endpoint_info['secure'],
                             http_client=http_client)
        try:
            return client.fget_object(endpoint_info['bucket'], endpoint_info['object_key'], filepath)
        except Exception as e:
            raise exceptions.PluginError(message=_('failed to download file[%(filepath)s] from s3: %(reason)s') % {
                'filepath': endpoint_info['object_key'],
                'reason': str(e)
            })

    def download_stream(self, url):
        endpoint_info = self.parse_url(url)
        ca_certs = os.environ.get('SSL_CERT_FILE') or certifi.where()
        http_client = urllib3.PoolManager(timeout=3,
                                          maxsize=10,
                                          cert_reqs='CERT_REQUIRED',
                                          ca_certs=ca_certs,
                                          retries=urllib3.Retry(total=3,
                                                                backoff_factor=0.2,
                                                                status_forcelist=[500, 502, 503, 504]))
        client = minio.Minio(endpoint_info['host'],
                             self.access_key,
                             self.secret_key,
                             secure=endpoint_info['secure'],
                             http_client=http_client)
        try:
            # urllib3.response.HTTPResponse
            response = client.get_object(endpoint_info['bucket'], endpoint_info['object_key'])
            return response, int(response.headers.get("content-length"))
        except Exception as e:
            raise exceptions.PluginError(message=_('failed to download file[%(filepath)s] from s3: %(reason)s') % {
                'filepath': endpoint_info['object_key'],
                'reason': str(e)
            })


if __name__ == '__main__':
    print(S3Client.parse_url('127.0.0.1:9000'))
    print(S3Client.parse_url('127.0.0.1'))
    print(S3Client.parse_url('http://127.0.0.1:9000'))
    print(S3Client.parse_url('https://127.0.0.1:9000'))
    print(S3Client.parse_url('s3://127.0.0.1:9000'))
    print(S3Client.parse_url('127.0.0.1/bucket'))
    print(S3Client.parse_url('127.0.0.1/bucket/dir1/filename.postfix'))
    print(S3Client.parse_url('127.0.0.1/bucket/dir1/dir2/filename.postfix'))
    print(S3Client.parse_url('http://127.0.0.1:9000/bucket/asset_id/session.cast'))
    print(S3Client.parse_url('127.0.0.1:9000/bucket/asset_id/session.cast'))
