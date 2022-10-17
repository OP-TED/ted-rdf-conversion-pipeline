import pysftp

from ted_sws import config
from ted_sws.notice_publisher.adapters.sftp_publisher_abc import SFTPPublisherABC


class SFTPPublisher(SFTPPublisherABC):
    """

    """

    def __init__(self, hostname: str = None, username: str = None, password: str = None, port: int = None):
        """Constructor Method"""
        self.hostname = hostname if hostname else config.SFTP_HOST
        self.username = username if username else config.SFTP_USER
        self.password = password if password else config.SFTP_PASSWORD
        self.port = port if port else config.SFTP_PORT
        self.connection = None
        self.is_connected = False

    def connect(self):
        """Connects to the sftp server and returns the sftp connection object"""

        cnopts = pysftp.CnOpts()
        # TODO: to be checked/removed when SSL will be setup
        cnopts.hostkeys = None
        # Get the sftp connection object
        self.connection = pysftp.Connection(
            host=self.hostname,
            username=self.username,
            password=self.password,
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
