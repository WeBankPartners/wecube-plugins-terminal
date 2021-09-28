# coding=utf-8

from __future__ import absolute_import
import logging
import socket
import time
import re
import datetime
import json
import os.path
import random

import jwt
import tornado.websocket
import tornado.web
import tornado.httpserver
import tornado.options
from tornado.ioloop import IOLoop
from talos.core import exceptions as base_ex
from talos.core import config
from talos.core import utils
from talos.common import cache
from talos.core.i18n import _
import zmq

from terminal.common import ssh
from terminal.common import exceptions
from terminal.common import wecube

from terminal.apps.assets import api as asset_api

LOG = logging.getLogger(__name__)
CONF = config.CONF
INTERVAL_CLOSE_CHECK = 0.5
INTERVAL_IDLE_CHECK = 1.0
TOKEN_KEY = 'terminal_subsystem_token'


class SSHHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self._auth_user = None
        self._asset_info = None
        self._ssh_client = ssh.SSHClient()
        self._ssh_meta = None
        self._timer_client_close_check = None
        self._timer_client_idle_check = None
        self._last_transfer = time.time()
        self._ssh_recorder = None
        self._ssh_recorder_db = None
        self._audit = ssh.CommandParser()
        zmq_socket = application.zmq_context.socket(zmq.PUSH)
        zmq_socket.connect(CONF.ipc.bind)
        self.event_pusher = zmq_socket

    def check_origin(self, origin):
        return True

    def open(self):
        pass

    def _encode(self, data):
        # if isinstance(data, bytes):
        #     return base64.b64encode(data).decode('utf-8')
        # else:
        #     return base64.b64encode(data.encode('utf-8')).decode('utf-8')
        if isinstance(data, bytes):
            return data.decode('utf-8', errors='replace')
        return data

    def _client_close_check(self):
        if self._ssh_client.is_shell_closed:
            self.close()
        else:
            self._timer_client_close_check = IOLoop.current().call_later(INTERVAL_CLOSE_CHECK, self._client_close_check)

    def _client_idle_check(self):
        if time.time() - self._last_transfer >= float(CONF.session.idle_timeout):
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
        if self._ssh_recorder:
            # close record file
            self._ssh_recorder.close()
            if self._ssh_recorder_db:
                asset_api.SessionRecord().update(self._ssh_recorder_db['id'], {
                    'ended_time': datetime.datetime.now(),
                    'filesize': os.path.getsize(self._ssh_recorder.filepath)
                })
            # push task to uploader
            self.event_pusher.send_json({
                'session_id':
                self._ssh_recorder_db['id'],
                'filepath':
                self._ssh_recorder.filepath,
                'object_key':
                self._asset_info['id'] + '/' + os.path.basename(self._ssh_recorder.filepath)
            })
            self.event_pusher.close()
            # reset pointer
            self._ssh_recorder = None
            self._ssh_recorder_db = None
        # if any exception happened, we should cancel all timers
        if self._timer_client_close_check:
            IOLoop.current().remove_timeout(self._timer_client_close_check)
        if self._timer_client_idle_check:
            IOLoop.current().remove_timeout(self._timer_client_idle_check)
        self._asset_info = None
        self._auth_user = None

    def on_message(self, message):
        '''call when received a message from client

        :param message: message format: {"type": "init/resize/console/listdir", "data": ""}
        :type message: dict
        '''
        def _generate_random(length=8):
            chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
            nonce = ''
            for idx in range(length):
                nonce += random.choice(chars)
            return nonce

        msg = json.loads(message)
        if msg['type'] == 'init':
            self._ssh_meta = msg['data']
            user_cols = self._ssh_meta.get('cols', None)
            user_rows = self._ssh_meta.get('rows', None)
            asset_id = self._ssh_meta.get('asset_id', None)
            token = self._ssh_meta.get('token', None)
            token_info = jwt.decode(token, verify=False)
            token_user = token_info['sub']
            _authority = token_info.get('authority', None) or '[]'
            token_permissions = set(_authority.strip('[]').split(','))
            if not asset_id:
                self.write_message(json.dumps({'type': 'error', 'data': _('missing param: asset_id')}), binary=False)
                raise exceptions.FieldRequired(attribute='asset_id')
            try:
                asset = asset_api.Asset(token=token).get_connection_info(asset_id, auth_roles=token_permissions)
            except exceptions.core_ex.AuthError as e:
                self.write_message(json.dumps({'type': 'error', 'data': _('invalid token')}), binary=False)
                raise e
            except exceptions.NotFoundError as e:
                self.write_message(json.dumps({
                    'type': 'error',
                    'data': _('the resource(%(resource)s) you request not found') % {
                        'resource': 'Asset#' + asset_id
                    }
                }),
                                   binary=False)
                raise e
            try:
                jump_servers = asset_api.JumpServer().get_jump_servers(asset['ip_address'])
                conn_info = self._ssh_client.connect(asset['ip_address'],
                                                     asset['username'],
                                                     asset['password'],
                                                     port=asset['port'],
                                                     jump_servers=jump_servers)
                jump_server = conn_info['jump_server']
                if jump_server and (jump_server[0] != asset['ip_address'] or str(jump_server[1]) != str(asset['port'])):
                    jump_host, jump_port, jump_username, jump_password = jump_server
                    self.write_message(json.dumps({
                        'type':
                        'console',
                        'data':
                        self._encode('#' * 80 + '\r\nusing jump server: %s@%s:%s\r\n' %
                                     (jump_username, jump_host, jump_port) + '#' * 80 + '\r\n')
                    }),
                                       binary=False)
                self._asset_info = asset
                self._auth_user = token_user
            except exceptions.PluginError as e:
                self.write_message(json.dumps({'type': 'error', 'data': str(e)}), binary=False)
                raise e
            except socket.timeout as e:
                self.write_message(json.dumps({'type': 'error', 'data': str(e)}), binary=False)
                raise e
            self._ssh_client.create_shell(self, cols=user_cols, rows=user_rows)
            self._audit.resize(user_cols, user_rows)
            self._ssh_client.create_sftp()
            # generate record after meta information
            session_filename = "%s_%s_%s.cast" % (asset_id, int(time.time()), _generate_random())
            self._ssh_recorder = ssh.SSHRecorder(os.path.join(CONF.session.record_path, session_filename))
            self._ssh_recorder_db = asset_api.SessionRecord().create({
                'asset_id': asset_id,
                'filepath': session_filename,
                'user': token_user,
                'started_time': datetime.datetime.now(),
                'ended_time': None
            })
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
            user_confirm = msg.get('confirm', False)
            is_dangerous = False
            if command and not user_confirm and utils.bool_from_string(CONF.check_itsdangerous, default=True):
                try:
                    client = wecube.WeCubeClient(CONF.wecube.base_url, None)
                    subsys_token = cache.get_or_create(TOKEN_KEY, client.login_subsystem, expires=600)
                    client.token = subsys_token
                    check_data = {
                        "operator": self._auth_user,
                        "serviceName": "N/A",
                        "servicePath": "",
                        "entityType": CONF.asset.asset_type,
                        "entityInstances": [{
                            "id": self._asset_info['id'],
                            'displayName': self._asset_info['display_name']
                        }],
                        "inputParams": {},
                        "scripts": [{
                            "type": None,
                            "content": command,
                            "name": "console input"
                        }]
                    }
                    box_ids = re.split(r',|\||;', CONF.boxes_check)
                    if len(box_ids) == 1 and not box_ids[0].isnumeric():
                        box_ids = None
                    resp_json = client.post(client.server + '/itsdangerous/v1/detection',
                                            check_data,
                                            param={'boxes': box_ids})
                    if resp_json['data']['text']:
                        is_dangerous = True
                        self.write_message(json.dumps({
                            'type': 'warn',
                            'data': resp_json['data']['text']
                        }),
                                           binary=False)
                except base_ex.Error as e:
                    # error if package itsdangerout not running, or timeout
                    # all command consider dangerous
                    is_dangerous = True
                    self.write_message(json.dumps({
                        'type': 'error',
                        'data': _('error calling itsdangerous: %(reason)s') % {
                            'reason': str(e)
                        }
                    }),
                                       binary=False)
            # reset audit
            if command and not is_dangerous:
                self._audit.reset()
            if not self._ssh_client.is_shell_closed:
                self._last_transfer = time.time()
                if not is_dangerous:
                    self._ssh_client.send_shell(msg['data'])
            else:
                self.close()
        elif msg['type'] == 'listdir':
            # update idle time
            self._last_transfer = time.time()
            dirpath = msg.get('data', None) or '~'
            results = {'pwd': dirpath, 'filelist': []}
            try:
                self._ssh_client.sftp.chdir(dirpath)
                dirpath = self._ssh_client.sftp.getcwd()
                results['pwd'] = dirpath
                for attr in self._ssh_client.sftp.listdir_attr(dirpath):
                    results['filelist'].append(ssh.SSHClient.format_sftp_attr(dirpath, attr))
            except FileNotFoundError as e:
                self.write_message(json.dumps({
                    'type': 'error',
                    'data': _('cannot open directory "%(name)s": File not found') % {
                        'name': dirpath
                    }
                }),
                                   binary=False)
            except PermissionError as e:
                self.write_message(json.dumps({
                    'type': 'error',
                    'data': _('cannot open directory "%(name)s": Permission denied') % {
                        'name': dirpath
                    }
                }),
                                   binary=False)
            results['filelist'].sort(key=lambda x: x['name'])
            if dirpath != '/':
                root_attr = ssh.SSHClient.format_sftp_attr(None, None)
                root_attr['name'] = '..'
                root_attr['mode'] = '----------'
                root_attr['fullpath'] = os.path.dirname(dirpath)
                root_attr['type'] = ssh.FileType.T_DIR
                results['filelist'].insert(0, root_attr)
            self.write_message(json.dumps({'type': 'listdir', 'data': results}), binary=False)
