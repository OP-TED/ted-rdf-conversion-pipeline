import pysftp

from ted_sws.notice_publisher.adapters.notice_publisher_abc import NoticePublisherABC
from ted_sws import config


class SFTPNoticePublisher(NoticePublisherABC):
    connection: pysftp.Connection = None
    default_host = config.SFTP_HOST
    default_user = config.SFTP_USER
    default_pass = config.SFTP_PASSWORD
    default_port = config.SFTP_PORT

    def __init__(self, hostname=default_host, username=default_user, password=default_pass, port=default_port,
                 remote_path=None):
        """Constructor Method"""
        # Set connection object to None (initial value)
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port or self.default_port
        self.remote_path = remote_path

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

    def disconnect(self):
        """Closes the sftp connection"""
        self.connection.close()

    def publish(self, source_path, remote_path=None) -> bool:
        return self.upload(source_path, remote_path)

    def upload(self, source_path, remote_path=None) -> bool:
        """
       Uploads the notice's METS manifestation to the sftp server remote path.
       """
        if remote_path is None:
            remote_path = self.remote_path

        if remote_path is None:
            raise ValueError("No remote path specified.")

        try:
            self.connection.put(source_path, remote_path)
            return True
        except Exception as err:
            raise Exception(err)

    def remove(self, remote_path) -> bool:
        try:
            self.connection.unlink(remote_path)
            return True
        except Exception as err:
            raise Exception(err)
