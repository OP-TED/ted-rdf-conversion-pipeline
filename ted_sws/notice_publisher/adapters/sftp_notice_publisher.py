import io

import paramiko
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

        self._sftp = None
        self._ssh = None




    def connect(self):
        """Connects to the sftp server and returns the sftp connection object"""

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(self.hostname, username=self.username,
                           pkey=self.private_key, port=self.port)
        self._ssh = ssh_client
        self._sftp = ssh_client.open_sftp()
        self.is_connected = True

    def disconnect(self):
        """Closes the sftp connection"""
        if self.is_connected:
            self._sftp.close()
            self._ssh.close()
            self._sftp = None
            self._ssh = None
            self.is_connected = False

    def __del__(self):
        self.disconnect()

    def publish(self, source_path: str, remote_path: str) -> bool:
        """
        Publish file_content to the sftp server remote path.
       """
        self._sftp.put(source_path, remote_path)
        return True

    def remove(self, remote_path: str) -> bool:
        """

        """
        self._sftp.remove(remote_path)
        return True
