import tempfile

import pytest

from ted_sws import config
from ted_sws.notice_publisher.adapters.notice_publisher import NoticePublisherFactory, Publisher
from ted_sws.notice_publisher.adapters.sftp_notice_publisher import SFTPNoticePublisher


def test_notice_publisher():
    with pytest.raises(Exception):
        NoticePublisherFactory.get_publisher(publisher=Publisher.SFTP, hostname=None)
    NoticePublisherFactory.get_publisher(publisher=Publisher.SFTP, hostname="HOST", username="USER", password="PASS",
                                         port=0, remote_path="")


def test_sftp_notice_publisher():
    user = config.SFTP_USER
    password = config.SFTP_PASSWORD
    host = None
    port = 0

    sftp_publisher = SFTPNoticePublisher(hostname=host, username=user, password=password, port=port, remote_path=None)

    with pytest.raises(Exception):
        sftp_publisher.connect()

    sftp_publisher.hostname = config.SFTP_HOST
    sftp_publisher.port = int(config.SFTP_PORT)
    sftp_publisher.connect()

    source_file = tempfile.NamedTemporaryFile()
    source_file.write(bytes("NOTICE", encoding='utf-8'))

    invalid_remote_path = "/upload"
    remote_path = "/upload/sftp_notice.zip"

    with pytest.raises(Exception):
        sftp_publisher.remove(remote_path)

    with pytest.raises(Exception):
        sftp_publisher.publish(source_file.name + "invalid", invalid_remote_path)

    with pytest.raises(ValueError):
        sftp_publisher.publish(source_file.name, None)

    published = sftp_publisher.publish(source_file.name, remote_path)
    assert published
    assert sftp_publisher.connection.exists(remote_path)
    sftp_publisher.remove(remote_path)
    assert not sftp_publisher.connection.exists(remote_path)

    sftp_publisher.disconnect()
