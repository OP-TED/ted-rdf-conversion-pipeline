import pysftp

from ted_sws import config
from ted_sws.notice_publisher.adapters.sftp_publisher_abc import SFTPPublisherABC
import tempfile


class SFTPPublisher(SFTPPublisherABC):
    """

    """

    def __init__(self, hostname: str = None, username: str = None, password: str = None, port: int = None,
                 private_key: str = None, private_key_passphrase: str = None, known_hosts: str = None):
        """Constructor Method"""
        self.hostname = hostname if hostname else config.SFTP_PUBLISH_HOST
        self.username = username if username else config.SFTP_PUBLISH_USER
        self.password = password if password else config.SFTP_PUBLISH_PASSWORD
        self.private_key_passphrase = private_key_passphrase if private_key_passphrase else config.SFTP_PRIVATE_KEY_PASSPHRASE
        self.port = port if port else config.SFTP_PUBLISH_PORT
        self.connection = None
        self.is_connected = False
        self.private_key = private_key if private_key else config.SFTP_PRIVATE_KEY
        self.known_hosts = known_hosts if known_hosts else config.SFTP_KNOWN_HOSTS
        self.known_hosts_file = None
        self.private_key_file = None

    def connect(self):
        """Connects to the sftp server and returns the sftp connection object"""

        self.known_hosts_file = tempfile.NamedTemporaryFile()
        self.private_key_file = tempfile.NamedTemporaryFile()
        self.known_hosts_file.write(self.known_hosts.encode(encoding="utf-8"))
        self.private_key_file.write(self.private_key.encode(encoding="utf-8"))
        cnopts = pysftp.CnOpts(knownhosts=self.known_hosts_file.name)
        # Get the sftp connection object
        self.connection = pysftp.Connection(
            host=self.hostname,
            username=self.username,
            password=self.password,
            private_key=self.private_key_file.name,
            private_key_pass=self.private_key_passphrase,
            port=self.port,
            cnopts=cnopts
        )

        self.is_connected = True

    def disconnect(self):
        """Closes the sftp connection"""
        if self.is_connected:
            self.connection.close()
            self.known_hosts_file.close()
            self.private_key_file.close()
            self.is_connected = False
            self.known_hosts_file = None
            self.private_key_file = None

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
