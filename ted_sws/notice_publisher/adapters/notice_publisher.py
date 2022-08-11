from enum import Enum

from ted_sws.notice_publisher.adapters.notice_publisher_abc import NoticePublisherABC
from ted_sws.notice_publisher.adapters.sftp_notice_publisher import SFTPNoticePublisher
from ted_sws import config


class Publisher(Enum):
    SFTP = "sftp"


DEFAULT_PUBLISHER = Publisher.SFTP


class NoticePublisherFactory:
    @classmethod
    def get_publisher(cls, publisher: Publisher = DEFAULT_PUBLISHER, **kwargs) -> NoticePublisherABC:
        """Factory Method to return the needed Publisher, based on """

        if publisher == Publisher.SFTP:
            hostname = kwargs['hostname'] if 'hostname' in kwargs else config.SFTP_HOST
            username = kwargs['username'] if 'username' in kwargs else config.SFTP_USER
            password = kwargs['password'] if 'password' in kwargs else config.SFTP_PASSWORD
            port = kwargs['port'] if 'port' in kwargs else config.SFTP_PORT
            remote_path = kwargs['remote_path'] if 'remote_path' in kwargs else None
            if not hostname or not username or not password:
                raise Exception("SFTPPublisher mandatory init parameters: (host, username, password)")
            return SFTPNoticePublisher(hostname=hostname, username=username, password=password, port=port,
                                       remote_path=remote_path)
