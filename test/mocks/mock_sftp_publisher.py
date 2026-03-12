from typing import Dict

from paramiko.ssh_exception import SSHException
from src.ted_sws.notice_publisher.adapters.sftp_publisher_abc import SFTPPublisherABC


class MockSFTPPublisherWithLimitedConnections(SFTPPublisherABC):
    _connection_count = 0
    _published_files: Dict[str, bytes] = {}

    def __init__(self, connection_threshold=2):
        self.connection_threshold = connection_threshold
        self.is_connected = False

    def connect(self):
        if self._connection_count >= self.connection_threshold:
            raise SSHException("Error: Too many connections. Connection closed by remote host.")

        self._connection_count += 1
        self.is_connected = True

    def disconnect(self):
        if self.is_connected:
            self.is_connected = False

    def publish(self, source_path, remote_path):
        if not self.is_connected:
            raise SSHException("Connection not established")

        try:
            with open(source_path, 'rb') as f:
                content = f.read()
                self._published_files[remote_path] = content
        except FileNotFoundError:
            raise IOError(f"Source file not found: {source_path}")

        return True

    def remove(self, remote_path):
        if not self.is_connected:
            raise SSHException("Connection not established")

        if remote_path not in self._published_files:
            raise IOError(f"Remote file not found: {remote_path}")

        del self._published_files[remote_path]
        return True

    def exists(self, remote_path):
        if not self.is_connected:
            raise SSHException("Connection not established")

        return remote_path in self._published_files
