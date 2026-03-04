import json
import threading
import urllib3
from typing import Optional

from kubernetes import client
from kubernetes.stream import stream
from kubernetes.client import Configuration, ApiClient
from tornado.ioloop import IOLoop


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PodClient:
    """
    K8s Pod Terminal Client

    特性：
    - 长期 Token
    - verify_ssl=False
    - 独立读取线程
    - Tornado IOLoop 回调派发
    - forward_stream.send(data)
    - 优雅关闭
    """

    def __init__(
        self,
        io_loop: Optional[IOLoop] = None,
    ):
        self.api_server = None
        self.token = None
        self.namespace = 'default'
        self.pod_name = None
        self.container = None

        self.io_loop = io_loop or IOLoop.current()

        self.api = None
        self.ws_client = None
        self.forward_stream = None

        self._reader_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._closed = True
        self._lock = threading.Lock()

    # ==========================================================
    # 初始化 API Client
    # ==========================================================

    def connect(self,
                api_server: str,
                token: str,
                namespace: str,
                pod_name: str,
                container: Optional[str] = None):
        self.api_server = api_server.rstrip("/")
        # Ensure api_server has a protocol scheme (default to https)
        if not self.api_server.startswith(('http://', 'https://')):
            self.api_server = f'https://{self.api_server}'
        self.token = token
        configuration = Configuration()
        configuration.host = self.api_server
        configuration.verify_ssl = False
        configuration.ssl_ca_cert = None
        configuration.api_key = {
            "authorization": "Bearer " + self.token
        }

        api_client = ApiClient(configuration)
        self.api = client.CoreV1Api(api_client)
        self.namespace = namespace
        self.pod_name = pod_name
        self.container = container

    # ==========================================================
    # 创建 Shell
    # ==========================================================

    def create_shell(
        self,
        forward_stream,
        term: str = "xterm",
        cols: Optional[int] = None,
        rows: Optional[int] = None,
        command=None,
    ):
        """
        forward_stream 必须提供 send(data: bytes) 方法
        """

        if not self.api:
            raise RuntimeError("Call connect() first")

        if command is None:
            command = ["/bin/bash"]

        self.forward_stream = forward_stream

        self.ws_client = stream(
            self.api.connect_get_namespaced_pod_exec,
            self.pod_name,
            self.namespace,
            container=self.container,
            command=command,
            stderr=True,
            stdin=True,
            stdout=True,
            tty=True,
            _preload_content=False,
        )

        self._closed = False
        self._stop_event.clear()

        # 如果初始化时给了 rows/cols，立即 resize
        if cols and rows:
            self.resize_shell(cols, rows)

        self._reader_thread = threading.Thread(
            target=self._read_loop,
            name=f"PodClient-{self.pod_name}",
            daemon=True,
        )
        self._reader_thread.start()

    # ==========================================================
    # 发送输入
    # ==========================================================

    def send_shell(self, data: bytes):
        with self._lock:
            if not self.ws_client or not self.ws_client.is_open():
                raise RuntimeError("Shell not open")

            if isinstance(data, bytes):
                data = data.decode()

            self.ws_client.write_stdin(data)

    def send_keepalive(self):
        """Send keepalive to prevent K8s WebSocket timeout (2min default)

        Writes to channel 4 (resize channel) which is designed for control messages
        and won't produce any visible output in the terminal or interfere with
        idle timeout detection.
        """
        with self._lock:
            if not self.ws_client or not self.ws_client.is_open():
                return

            try:
                # Write empty string to channel 4 (resize/control channel)
                # This keeps the connection alive without:
                # 1. Displaying anything in terminal (not stdin)
                # 2. Producing stdout/stderr output (won't trigger _dispatch)
                # 3. Interfering with idle timeout (no data sent to user)
                self.ws_client.write_channel(4, '')
            except Exception:
                # If write fails, connection might be dead anyway
                pass

    # ==========================================================
    # Resize
    # ==========================================================

    def resize_shell(self, width: int, height: int):
        with self._lock:
            if not self.ws_client or not self.ws_client.is_open():
                return

            payload = json.dumps({
                "Width": width,
                "Height": height
            })

            self.ws_client.write_channel(4, payload)

    # ==========================================================
    # 是否关闭
    # ==========================================================

    @property
    def is_shell_closed(self) -> bool:
        return self._closed

    # ==========================================================
    # 阻塞读取线程
    # ==========================================================

    def _read_loop(self):
        try:
            while (
                not self._stop_event.is_set()
                and self.ws_client
                and self.ws_client.is_open()
            ):
                # 阻塞等待数据
                self.ws_client.update(timeout=1)

                if self.ws_client.peek_stdout():
                    data = self.ws_client.read_stdout()
                    self._dispatch(data)

                if self.ws_client.peek_stderr():
                    data = self.ws_client.read_stderr()
                    self._dispatch(data)

        except Exception as e:
            self._dispatch_error(e)

        finally:
            self._closed = True
            self._safe_close_ws()

    # ==========================================================
    # 数据派发（主线程执行）
    # ==========================================================

    def _dispatch(self, data: str):
        if not self.forward_stream:
            return

        payload = data.encode()

        self.io_loop.add_callback(
            self._safe_send,
            payload,
        )

    def _dispatch_error(self, error: Exception):
        if not self.forward_stream:
            return

        payload = f"\n[PodClient Error] {error}\n".encode()

        self.io_loop.add_callback(
            self._safe_send,
            payload,
        )

    def _safe_send(self, data: bytes):
        try:
            self.forward_stream.send(data)
        except Exception:
            # 前端断开或 write_message 失败
            self.close()

    # ==========================================================
    # 优雅关闭
    # ==========================================================

    def close(self, timeout: float = 3.0):
        if self._closed:
            return

        self._stop_event.set()
        self._safe_close_ws()

        if self._reader_thread and self._reader_thread.is_alive():
            self._reader_thread.join(timeout=timeout)

        self._closed = True

    def _safe_close_ws(self):
        with self._lock:
            if self.ws_client:
                try:
                    self.ws_client.close()
                except Exception:
                    pass
                finally:
                    self.ws_client = None