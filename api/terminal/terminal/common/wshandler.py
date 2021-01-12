# coding=utf-8

from __future__ import absolute_import
import logging
import time
import json
import os.path

import tornado.websocket
import tornado.web
import tornado.httpserver
import tornado.options
from tornado.ioloop import IOLoop
from talos.core import config
from talos.core.i18n import _

from terminal.common import ssh
from terminal.common import exceptions
from terminal.apps.assets import api as asset_api

LOG = logging.getLogger(__name__)
CONF = config.CONF
INTERVAL_CLOSE_CHECK = 0.5
INTERVAL_IDLE_CHECK = 1.0


class SSHHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self._ssh_client = ssh.SSHClient()
        self._ssh_meta = None
        self._timer_client_close_check = None
        self._timer_client_idle_check = None
        self._last_transfer = time.time()
        self._ssh_recorder = ssh.SSHRecorder(os.path.join(CONF.session.record_path, "%s.cast" % int(time.time())))
        self._audit = ssh.CommandParser()

    def check_origin(self, origin):
        return True

    def open(self):
        self.request.get_query_argument('asset_id')
        asset_id = self.get_query_argument('asset_id')
        if not asset_id:
            self.set_status(400)
            self.write({'code': 400, 'status': 'ERROR', 'data': None, 'message': _('missing query param: asset_id')})
            self.close()
            return
        try:
            asset = asset_api.Asset().get_connection_info(asset_id)
        except exceptions.NotFoundError:
            self.set_status(400)
            self.write({
                'code': 400,
                'status': 'ERROR',
                'data': None,
                'message': _('the resource(%(resource)s) you request not found') % {
                    'resource': 'Asset#' + asset_id
                }
            })
            self.close()
            return
        self._ssh_client.connect(asset['ip_address'], asset['username'], asset['password'])

    def _encode(self, data):
        # if isinstance(data, bytes):
        #     return base64.b64encode(data).decode('utf8')
        # else:
        #     return base64.b64encode(data.encode('utf8')).decode('utf8')
        if isinstance(data, bytes):
            return data.decode('utf8')
        return data

    def _client_close_check(self):
        if self._ssh_client.is_shell_closed:
            self.close()
        else:
            self._timer_client_close_check = IOLoop.current().call_later(INTERVAL_CLOSE_CHECK, self._client_close_check)

    def _client_idle_check(self):
        if time.time() - self._last_transfer >= CONF.session.idle_timeout:
            self.write_message(json.dumps({
                'type':
                'console',
                'data':
                self._encode('\r\ndisconnect for idle session(%s secs)' % CONF.session.idle_timeout)
            }),
                               binary=False)
            self.close()
        else:
            self._timer_client_idle_check = IOLoop.current().call_later(INTERVAL_IDLE_CHECK, self._client_idle_check)

    def send(self, data):
        self._last_transfer = time.time()
        self._audit.feed('output', data)
        self.write_message(json.dumps({'type': 'console', 'data': self._encode(data)}), binary=False)
        self._ssh_recorder.write_command(None, data)

    def on_close(self):
        self._ssh_client.close()
        self._ssh_recorder.close()
        # if any exception happened, we should cancel all timers
        if self._timer_client_close_check:
            IOLoop.current().remove_timeout(self._timer_client_close_check)
        if self._timer_client_idle_check:
            IOLoop.current().remove_timeout(self._timer_client_idle_check)

    def on_message(self, message):
        '''call when received a message from client

        :param message: message format: {"type": "init/resize/console/listdir", "data": ""}
        :type message: dict
        '''
        msg = json.loads(message)
        if msg['type'] == 'init':
            self._ssh_meta = msg['data']
            user_cols = self._ssh_meta.get('cols', None)
            user_rows = self._ssh_meta.get('rows', None)
            self._ssh_client.create_shell(self, cols=user_cols, rows=user_rows)
            self._audit.resize(user_cols, user_rows)
            self._ssh_client.create_sftp()
            # generate record after meta information
            self._ssh_recorder.start(cols=user_cols, rows=user_rows)
            self._timer_client_close_check = IOLoop.current().call_later(INTERVAL_CLOSE_CHECK, self._client_close_check)
            self._timer_client_idle_check = IOLoop.current().call_later(INTERVAL_IDLE_CHECK, self._client_idle_check)
        elif msg['type'] == 'resize':
            user_cols = msg['data']['cols']
            user_rows = msg['data']['rows']
            self._ssh_client.resize_shell(user_cols, user_rows)
            self._audit.resize(user_cols, user_rows)
        elif msg['type'] == 'console':
            # NOTE: send will write back all command, but how can we seperate user inputs from outputs?
            # self._ssh_recorder.write_command(msg['data'], None)
            command = self._audit.feed('input', msg['data'])
            if command:
                # TODO: check command if is dangerous?
                self.write_message(json.dumps({'type': 'warn', 'data': command}), binary=False)

            if not self._ssh_client.is_shell_closed:
                self._last_transfer = time.time()
                self._ssh_client.send_shell(msg['data'])
            else:
                self.close()
        elif msg['type'] == 'listdir':
            # update idle time
            self._last_transfer = time.time()
            dirpath = msg.get('data', None) or '~'
            self._ssh_client.sftp.chdir(dirpath)
            dirpath = self._ssh_client.sftp.getcwd()
            results = []
            for attr in self._ssh_client.sftp.listdir_attr(dirpath):
                results.append(ssh.SSHClient.format_sftp_attr(dirpath, attr))
            if dirpath != '/':
                root_attr = ssh.SSHClient.format_sftp_attr(None, None)
                root_attr['name'] = '..'
                root_attr['fullpath'] = os.path.dirname(dirpath)
                root_attr['isdir'] = True
                results.insert(0, root_attr)
            self.write_message(json.dumps({'type': 'listdir', 'data': results}), binary=False)
