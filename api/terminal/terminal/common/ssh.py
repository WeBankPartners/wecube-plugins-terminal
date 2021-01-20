# coding=utf-8
"""
terminal.server.ssh
~~~~~~~~~~~~~~~~~~~

本模块提供SSH Shell Client & Shell Recorder服务能力

"""

from __future__ import absolute_import
import logging
import io
import functools
import tempfile
import time
import json
import stat
import os.path

import pyte
import paramiko
import paramiko.ssh_exception
from paramiko.common import x80000000, o700, o70, xffffffff
from tornado.ioloop import IOLoop
from talos.core.i18n import _
from terminal.common import exceptions

LOG = logging.getLogger(__name__)
RECV_BUFF_SIZE = 64 * 1024
DEFAULT_COLUMNS = 80
DEFAULT_ROWS = 24


class FileType:
    T_DIR = 'dir'
    T_FILE = 'file'
    T_LINK = 'link'
    T_SOCKET = 'socket'
    T_PIPE = 'pipe'
    T_CDEVICE = 'character-device'
    T_BDEVICE = 'block-device'
    T_DOOR = 'door'
    T_PORT = 'port'
    T_WHITEOUT = 'whiteout'


class SSHClient:
    def __init__(self):
        self._shell = None
        self._shell_fileno = None
        self._sftp = None
        self._client = paramiko.SSHClient()

    @property
    def sftp(self):
        return self._sftp

    def connect(self, host, username, password, port=22):
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self._client.connect(hostname=host, port=int(port), username=username, password=password, timeout=10.0)
        except paramiko.AuthenticationException as e:
            LOG.exception(e)
            raise exceptions.PluginError(message=_(
                "failed to authenticate %(username)s@%(host)s:%(port)s with password: %(password)s, detail: %(detail)s")
                                         % {
                                             'username': username,
                                             'host': host,
                                             'port': port,
                                             'password': len(password) * '*',
                                             'detail': e
                                         })
        except paramiko.SSHException as e:
            LOG.exception(e)
            raise exceptions.PluginError(message=_(
                "failed to connect %(username)s@%(host)s:%(port)s with password: %(password)s, detail: %(detail)s") % {
                    'username': username,
                    'host': host,
                    'port': port,
                    'password': len(password) * '*',
                    'detail': e
                })
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            LOG.exception(e)
            raise exceptions.PluginError(message=_("failed to establish connection on %(host)s:%(port)s") % {
                'host': host,
                'port': port
            })

    def _load_private_key(self, key_content, key_password):
        return paramiko.RSAKey.from_private_key(io.StringIO(key_content), key_password)

    def connect_pkey(self, host, username, key_content, key_password=None, port=22):
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self._client.connect(hostname=host,
                                 port=int(port),
                                 username=username,
                                 pkey=self._load_private_key(key_content, key_password),
                                 timeout=10.0)
        except paramiko.AuthenticationException as e:
            LOG.exception(e)
            raise exceptions.PluginError(message=_(
                "failed to authenticate %(username)s@%(host)s:%(port)s with private key, detail: %(detail)s") % {
                    'username': username,
                    'host': host,
                    'port': port,
                    'detail': e
                })
        except paramiko.SSHException as e:
            LOG.exception(e)
            raise exceptions.PluginError(
                message=_("failed to connect %(username)s@%(host)s:%(port)s with private key, detail: %(detail)s") % {
                    'username': username,
                    'host': host,
                    'port': port,
                    'detail': e
                })
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            LOG.exception(e)
            raise exceptions.PluginError(message=_("failed to establish connection on %(host)s:%(port)s") % {
                'host': host,
                'port': port
            })

    def create_shell(self, forward_stream, term="xterm", cols=None, rows=None):
        '''get shell from ssh client

        :param forward_stream: object with send(data) method, anything output from shell will send to forward_stream
        :type forward_stream: any
        :param term: [description], defaults to "xterm"
        :type term: str, optional
        '''
        if self._shell:
            # only one shell active in a client
            IOLoop.current().remove_handler(self._shell_fileno)
            self._shell.close()
        cols = cols or DEFAULT_COLUMNS
        rows = rows or DEFAULT_ROWS
        self._shell = self._client.invoke_shell(term, width=cols, height=rows)
        self._shell.setblocking(0)
        self._shell_fileno = self._shell.fileno()
        IOLoop.current().add_handler(self._shell_fileno, functools.partial(self._backward, forward_stream), IOLoop.READ)

    def send_shell(self, data):
        if self._shell:
            self._shell.sendall(data)

    def close_shell(self):
        if self._shell:
            IOLoop.current().remove_handler(self._shell_fileno)
            self._shell.close()
            self._shell = None
            self._shell_fileno = None

    def create_sftp(self):
        if self._sftp:
            # only one sftp active in a client
            self._sftp.close()
        self._sftp = self._client.open_sftp()
        return self._sftp

    def close_sftp(self):
        if self._sftp:
            self._sftp.close()
            self._shell = None

    def resize_shell(self, cols, rows):
        if self._shell:
            self._shell.resize_pty(width=cols, height=rows)

    def _backward(self, forward_stream, fd, events):
        while self._shell.recv_ready():
            data = self._shell.recv(RECV_BUFF_SIZE)
            forward_stream.send(data)
        while self._shell.recv_stderr_ready():
            data = self._shell.recv_stderr(RECV_BUFF_SIZE)
            forward_stream.send(data)

    def close(self):
        self.close_shell()
        self.close_sftp()
        self._client.close()

    @property
    def is_shell_closed(self):
        if self._shell:
            return self._shell.closed
        return True

    @classmethod
    def format_sftp_attr(cls, cwd, attr):
        def _compute_date(st_time):
            # compute display date
            datestr = ''
            if (st_time is None) or (st_time == xffffffff):
                # shouldn't really happen
                datestr = "(unknown date)"
            else:
                if abs(time.time() - st_time) > 15552000:
                    # (15552000 = 6 months)
                    datestr = time.strftime("%d %b %Y", time.localtime(st_time))
                else:
                    datestr = time.strftime("%d %b %H:%M", time.localtime(st_time))
            return datestr

        result = {
            'name': '',
            'fullpath': '',
            'mode': '',
            'type': None,
            'size': 0,
            'gid': 0,
            'uid': 0,
            'atime': '',
            'mtime': ''
        }
        if attr is not None:
            result['name'] = getattr(attr, "filename", "?")
            result['fullpath'] = os.path.join(cwd, result['name'])
            ks = "?---------"
            if attr.st_mode is not None:
                ks = stat.filemode(attr.st_mode)
            else:
                ks = "?---------"
            result['mode'] = ks
            if attr.st_mode is not None:
                if stat.S_ISDIR(attr.st_mode):
                    result['type'] = FileType.T_DIR
                elif stat.S_ISREG(attr.st_mode):
                    result['type'] = FileType.T_FILE
                elif stat.S_ISLNK(attr.st_mode):
                    result['type'] = FileType.T_LINK
                elif stat.S_ISSOCK(attr.st_mode):
                    result['type'] = FileType.T_SOCKET
                elif stat.S_ISFIFO(attr.st_mode):
                    result['type'] = FileType.T_PIPE
                elif stat.S_ISCHR(attr.st_mode):
                    result['type'] = FileType.T_CDEVICE
                elif stat.S_ISBLK(attr.st_mode):
                    result['type'] = FileType.T_BDEVICE
                elif stat.S_ISDOOR(attr.st_mode):
                    result['type'] = FileType.T_DOOR
                elif stat.S_ISPORT(attr.st_mode):
                    result['type'] = FileType.T_PORT
                elif stat.S_ISWHT(attr.st_mode):
                    result['type'] = FileType.T_WHITEOUT

            # not all servers support uid/gid
            uid = attr.st_uid
            gid = attr.st_gid
            size = attr.st_size
            if uid is None:
                uid = 0
            if gid is None:
                gid = 0
            if size is None:
                size = 0
            result['size'] = size
            result['gid'] = gid
            result['uid'] = uid
            result['atime'] = _compute_date(attr.st_atime)
            result['mtime'] = _compute_date(attr.st_mtime)
        return result


class SSHRecorder:
    '''record everything to file, using format:
    https://github.com/asciinema/asciinema/blob/develop/doc/asciicast-v2.md
    '''
    def __init__(self, filepath=None):
        self._start_time = None
        self._filepath = filepath
        self._fileobj = None

    def start(self, cols=None, rows=None):
        '''start recording, it will write header line to record file. 

        :param cols: num of columns, defaults to None(as 80)
        :type cols: int, optional
        :param rows: num of rows, defaults to None(as 24)
        :type rows: int, optional
        '''
        cols = cols or DEFAULT_COLUMNS
        rows = rows or DEFAULT_ROWS
        if self._filepath:
            self._fileobj = open(self._filepath, 'w+')
        else:
            self._fileobj = tempfile.TemporaryFile('w+')
        LOG.info('generating terminal-record file: %s', self._fileobj.name)
        self._start_time = time.time()
        header = {"version": 2, "width": cols, "height": rows, "timestamp": self._start_time, "env": {}}
        header = json.dumps(header) + '\n'
        self._fileobj.write(header)

    def write_command(self, input_content, output_content):
        # start as default meta info if user not calling start()
        if not self._start_time:
            self.start()
        # eg. [5.402543, "o", "\u001b[?1000h\u001b[39;49m\u001b[37m\u001b[40m\u001b[H\u001b[2J"]
        if isinstance(input_content, bytes):
            input_content = input_content.decode('utf8')
        if isinstance(output_content, bytes):
            output_content = output_content.decode('utf8')
        if input_content is not None:
            self._fileobj.write(json.dumps([str(time.time() - self._start_time), "i", input_content]) + '\n')
        if output_content is not None:
            self._fileobj.write(json.dumps([time.time() - self._start_time, "o", output_content]) + '\n')

    def close(self, read_content=False):
        content = None
        if self._fileobj:
            LOG.info('closing terminal-record file: %s', self._fileobj.name)
            self._fileobj.flush()
            if read_content:
                self._fileobj.seek(0, 0)
                content = self._fileobj.read()
            self._fileobj.close()
        self._start_time = None
        return content


class TerminalChar:
    CH_SOH = '\x03'  # Ctrl+C
    CH_SRH = '\x12'  # Ctrl+R
    CH_TAB = '\t'  # Tab
    CH_ENT = '\r'  # Enter
    CH_ESC = '\x1b'  # Enter

    ESC_MVUP = '\x1b[A'  # Move Up
    ESC_MVDOWN = '\x1b[B'  # Move Down


class CommandParser:
    def __init__(self):
        self.screen = pyte.Screen(DEFAULT_COLUMNS, DEFAULT_ROWS)
        self.stream = pyte.ByteStream(self.screen)
        self._state = None

    def resize(self, cols, rows):
        cols = cols or DEFAULT_COLUMNS
        rows = rows or DEFAULT_ROWS
        self.screen.resize(lines=rows, columns=cols)

    def feed(self, data_type, data):
        '''feed data, and return command to be execute if any

        :param data_type: input/output
        :type data_type: string
        :param data: data of input/output
        :type data: byte/unicode
        '''
        # ori_data = data
        # if isinstance(data, bytes):
        #     data = data.decode('utf8')
        if not data:
            return None
        if data_type == 'input':
            if data[0] == TerminalChar.CH_SOH:
                self.screen.reset()
            elif data[0] == TerminalChar.CH_SRH:
                # feed data from output
                self._state = TerminalChar.CH_SRH
            elif data[0] == TerminalChar.CH_TAB:
                # feed data from output
                self._state = TerminalChar.CH_TAB
            elif data[0] == TerminalChar.CH_ENT:
                # TODO: input with multiline data support
                # TODO: parse with multine data optimize
                # TODO: vim mode optimize
                command = "".join(self.screen.display).strip()
                self.screen.reset()
                if self._state == TerminalChar.CH_SRH + 'input':
                    parts = command.split(':')
                    if len(parts) == 2:
                        command = parts[1]
                self._state = None
                return command
            elif data == TerminalChar.ESC_MVUP:
                # feed data from output
                self._state = TerminalChar.ESC_MVUP
            elif data == TerminalChar.ESC_MVDOWN:
                # feed data from output
                self._state = TerminalChar.ESC_MVDOWN
            else:
                if self._state == TerminalChar.CH_SRH:
                    self._state = TerminalChar.CH_SRH + 'input'
                elif self._state is None:
                    self._state = 'input'
        if data_type == 'output' and self._state:
            if self._state == 'input':
                self._state = None
                self.stream.feed(data)
            elif self._state == TerminalChar.CH_TAB:
                if b'\r' not in data:
                    self.stream.feed(data)
                # tab state effect once
                self._state = None
            elif self._state == TerminalChar.CH_SRH or self._state == TerminalChar.CH_SRH + 'input':
                self.stream.feed(data)
            elif self._state == TerminalChar.ESC_MVUP:
                self.stream.feed(data)
            elif self._state == TerminalChar.ESC_MVDOWN:
                self.stream.feed(data)
        elif data_type == 'output' and self._state is None:
            # record control sequence, eg: vim
            if data[0] == TerminalChar.CH_ESC:
                self.stream.feed(data)