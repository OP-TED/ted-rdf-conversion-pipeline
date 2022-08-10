import pysftp

from ted_sws.core.model.notice import Notice
from ted_sws.notice_publisher.adapters.notice_publisher import NoticePublisherABC


class SFTPNoticePublisher(NoticePublisherABC):
    def __init__(self, hostname, username, password, port=22, remote_path=None):
        """Constructor Method"""
        # Set connection object to None (initial value)
        self.connection = None
        self.hostname = hostname
        self.username = username
        self.password = password
        self.remote_path = remote_path
        self.port = port

    def connect(self):
        """Connects to the sftp server and returns the sftp connection object"""

        try:
            # Get the sftp connection object
            self.connection = pysftp.Connection(
                host=self.hostname,
                username=self.username,
                password=self.password,
                port=self.port,
            )
        except Exception as err:
            raise Exception(err)

    def disconnect(self):
        """Closes the sftp connection"""
        self.connection.close()

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
