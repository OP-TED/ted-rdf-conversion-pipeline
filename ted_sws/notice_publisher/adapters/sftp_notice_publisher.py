import pysftp

from ted_sws import config
from ted_sws.notice_publisher.adapters.sftp_publisher_abc import SFTPPublisherABC


class SFTPPublisher(SFTPPublisherABC):
    """

    """

    connection: pysftp.Connection = None
    default_host = config.SFTP_HOST
    default_user = config.SFTP_USER
    default_pass = config.SFTP_PASSWORD
    default_port = config.SFTP_PORT

    def __init__(self, hostname=default_host, username=default_user, password=default_pass, port=default_port):
        """Constructor Method"""
        # Set connection object to None (initial value)
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.is_connected = False

    def connect(self):
        """Connects to the sftp server and returns the sftp connection object"""

        try:
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
        except Exception as err:
            raise Exception(err)

        self.is_connected = True

    def disconnect(self):
        """Closes the sftp connection"""
        if self.is_connected:
            self.connection.close()
            self.is_connected = False

    def __del__(self):
        self.disconnect()

    def publish(self, source_path, remote_path) -> bool:
        """
        Publish file_content to the sftp server remote path.
       """
        try:
            self.connection.put(source_path, remote_path)
            return True
        except Exception as err:
            raise Exception(err)

    def remove(self, remote_path) -> bool:
        """

        """
        try:
            self.connection.unlink(remote_path)
            return True
        except Exception as err:
            raise Exception(err)
