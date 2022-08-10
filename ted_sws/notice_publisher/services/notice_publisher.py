from ted_sws.notice_publisher.adapters.notice_publisher import NoticePublisherABC
from ted_sws.notice_publisher.adapters.sftp_notice_publisher import SFTPNoticePublisher
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepositoryABC
import base64
import tempfile


def publish_notice_package(notice: Notice, notice_publisher: NoticePublisherABC, notice_repository: NoticeRepositoryABC,
                           remote_path=None):
    mets_manifestation = notice.mets_manifestation
    if not mets_manifestation:
        raise ValueError("Notice does not have a METS manifestation to be published.")

    package_content = base64.b64decode(bytes(mets_manifestation.object_data), validate=True)

    source_file = tempfile.NamedTemporaryFile()
    source_file.write(package_content)

    if notice_publisher.upload(source_file, remote_path):
        notice.update_status_to(NoticeStatus.PUBLISHED)
        notice_repository.update(notice)
    else:
        raise Exception(f"Notice {notice.ted_id} could not be published.")


def publish_notice(notice: Notice, notice_repository: NoticeRepositoryABC, hostname, username, password,
                   remote_path=None, port=22):
    notice_publisher = SFTPNoticePublisher(hostname=hostname, username=username, password=password, port=port,
                                           remote_path=remote_path)
    notice_publisher.connect()
    publish_notice_package(notice, notice_publisher, notice_repository)
    notice_publisher.disconnect()
    pass
