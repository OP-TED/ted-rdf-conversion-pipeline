import tempfile

import pytest

from ted_sws import config
from ted_sws.notice_publisher.adapters.sftp_notice_publisher import SFTPPublisher
from ted_sws.notice_publisher.adapters.s3_notice_publisher import S3Publisher
import ssl


def test_sftp_notice_publisher():
    sftp_publisher = SFTPPublisher(port=123)

    with pytest.raises(Exception):
        sftp_publisher.connect()

    sftp_publisher.port = config.SFTP_PUBLISH_PORT
    sftp_publisher.connect()

    source_file = tempfile.NamedTemporaryFile()
    source_file.write(bytes("NOTICE", encoding='utf-8'))

    invalid_remote_path = "/upload"
    remote_path = "/upload/sftp_notice.zip"

    with pytest.raises(Exception):
        sftp_publisher.remove(remote_path)

    with pytest.raises(Exception):
        sftp_publisher.publish(source_file.name + "invalid", invalid_remote_path)

    with pytest.raises(Exception):
        sftp_publisher.publish(source_file.name, None)

    published = sftp_publisher.publish(source_file.name, remote_path)
    assert published
    assert sftp_publisher.connection.exists(remote_path)
    sftp_publisher.remove(remote_path)
    assert not sftp_publisher.connection.exists(remote_path)

    sftp_publisher.disconnect()


def test_s3_notice_publisher():
    s3_publisher = S3Publisher(ssl_verify=True)
    assert s3_publisher.client._http.connection_pool_kw['cert_reqs'] == ssl.CERT_REQUIRED.name

    s3_publisher = S3Publisher(ssl_verify=False)
    assert s3_publisher.client._http.connection_pool_kw['cert_reqs'] == ssl.CERT_NONE
