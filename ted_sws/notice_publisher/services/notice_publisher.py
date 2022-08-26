import base64
import pathlib
import tempfile

from ted_sws import config
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepositoryABC
from ted_sws.notice_publisher.adapters.sftp_notice_publisher import SFTPPublisher
from ted_sws.notice_publisher.adapters.sftp_publisher_abc import SFTPPublisherABC


def publish_notice(notice: Notice, publisher: SFTPPublisherABC = SFTPPublisher(),
                   remote_folder_path=config.SFTP_PATH) -> bool:
    """
        This function publishes the METS manifestation for a Notice in Cellar.
    """

    mets_manifestation = notice.mets_manifestation
    if not mets_manifestation or not mets_manifestation.object_data:
        raise ValueError("Notice does not have a METS manifestation to be published.")

    package_content = base64.b64decode(bytes(mets_manifestation.object_data, encoding='utf-8'), validate=True)
    remote_notice_path = f"{remote_folder_path}/{notice.ted_id}.zip"
    source_file = tempfile.NamedTemporaryFile()
    source_file.write(package_content)
    try:
        publisher.connect()
        if publisher.publish(source_path=pathlib.Path(source_file.name),
                             remote_path=remote_notice_path):
            notice.update_status_to(NoticeStatus.PUBLISHED)
        publisher.disconnect()
    except Exception as e:
        raise Exception(f"Notice {notice.ted_id} could not be published: " + str(e))

    return notice.status == NoticeStatus.PUBLISHED


def publish_notice_by_id(notice_id: str, notice_repository: NoticeRepositoryABC,
                         publisher: SFTPPublisherABC = SFTPPublisher(), remote_folder_path=config.SFTP_PATH) -> bool:
    """
        This function publishes the METS manifestation of a Notice, based on notice_id, in Cellar.
    """
    notice = notice_repository.get(reference=notice_id)
    result = publish_notice(notice=notice, publisher=publisher, remote_folder_path=remote_folder_path)
    if result:
        notice_repository.update(notice=notice)
    return result
