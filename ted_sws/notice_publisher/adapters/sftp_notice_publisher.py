import io

import paramiko
import pysftp

from ted_sws import config
from ted_sws.notice_publisher.adapters.sftp_publisher_abc import SFTPPublisherABC


class SFTPPublisher(SFTPPublisherABC):
    """

    """

    def __init__(self, hostname: str = None, username: str = None, password: str = None, port: int = None,
                 private_key: str = None, private_key_passphrase: str = None):
        """Constructor Method"""
        self.hostname = hostname if hostname else config.SFTP_PUBLISH_HOST
        self.username = username if username else config.SFTP_PUBLISH_USER
        self.password = password if password else config.SFTP_PUBLISH_PASSWORD
        self.port = port if port else config.SFTP_PUBLISH_PORT
        self.connection = None
        self.is_connected = False
        self.private_key = None
        self.private_key_passphrase = private_key_passphrase if private_key_passphrase else config.SFTP_PRIVATE_KEY_PASSPHRASE
        private_key = private_key if private_key else config.SFTP_PRIVATE_KEY
        if private_key:
            self.private_key = paramiko.RSAKey.from_private_key(io.StringIO(private_key),
                                                                password=self.private_key_passphrase)

        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(self.hostname, username=self.username,
                           pkey=self.private_key, port=self.port)
        self.host_keys = ssh_client.get_host_keys()
        ssh_client.close()

    def connect(self):
        """Connects to the sftp server and returns the sftp connection object"""

        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = self.host_keys
        # Get the sftp connection object
        self.connection = pysftp.Connection(
            host=self.hostname,
            username=self.username,
            password=self.password,
            private_key=self.private_key,
            private_key_pass=self.private_key_passphrase,
            port=self.port,
            cnopts=cnopts
        )

        self.is_connected = True

    def disconnect(self):
        """Closes the sftp connection"""
        if self.is_connected:
            self.connection.close()
            self.is_connected = False

    def __del__(self):
        self.disconnect()

    def publish(self, source_path: str, remote_path: str) -> bool:
        """
        Publish file_content to the sftp server remote path.
       """
        self.connection.put(source_path, remote_path)
        return True

    def remove(self, remote_path: str) -> bool:
        """

        """
        self.connection.unlink(remote_path)
        return True
