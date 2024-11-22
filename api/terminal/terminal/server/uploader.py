# coding=utf-8
"""
terminal.server.uploader
~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供会话审计异步上传S3 worker

"""

from __future__ import absolute_import

import os
import logging
from concurrent.futures import ThreadPoolExecutor as Executor

import zmq
from talos.core import config

from terminal.server.wsgi_server import application
from terminal.common import s3
from terminal.db import resource

CONF = config.CONF
LOG = logging.getLogger(__name__)


def upload(session_id, filepath, endpoint, ak, sk, bucket, object_key):
    if not os.path.exists(filepath):
        return
    client = s3.S3Client(endpoint, ak, sk)
    urlprefix = endpoint.rstrip('/')
    if not urlprefix.startswith('http'):
        urlprefix = 'http://' + urlprefix
    fullurl = '/'.join([urlprefix, bucket, object_key])
    try:
        client.upload_file(bucket, object_key, filepath)
        resource.SessionRecord().update(session_id, {'filepath': fullurl})
        LOG.info('session upload task[%s] successed', session_id)
        os.remove(filepath)
    except Exception as e:
        LOG.error('session upload task[%s] failed, leave it as file record', session_id)
        LOG.exception(e)


def main():
    workers = Executor(max_workers=20)
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind(CONF.ipc.bind)
    while True:
        try:
            msg = socket.recv_json()
            LOG.info('receive session upload task[%s]: %s', msg['session_id'], msg)
            if CONF.s3.server and CONF.s3.access_key and CONF.s3.secret_key and CONF.s3.bucket:
                workers.submit(upload, msg['session_id'], msg['filepath'], CONF.s3.server, CONF.s3.access_key,
                               CONF.s3.secret_key, CONF.s3.bucket, msg['object_key'])
            else:
                LOG.info('ignore session upload task[%s]: s3 information is not provide', msg['session_id'])
        except KeyboardInterrupt as e:
            return
        except Exception as e:
            LOG.exception(e)


if __name__ == '__main__':
    main()