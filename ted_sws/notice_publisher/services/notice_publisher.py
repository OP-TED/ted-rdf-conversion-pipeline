import base64
import tempfile
from pathlib import Path
from typing import Union

from ted_sws import config
from ted_sws.core.model.notice import Notice, NoticeStatus, UnsupportedStatusTransition
from ted_sws.data_manager.adapters.notice_repository import NoticeRepositoryABC
from ted_sws.notice_packager.adapters.archiver import ARCHIVE_DEFAULT_FORMAT
from ted_sws.notice_publisher.adapters.notice_publisher import NoticePublisherFactory
from ted_sws.notice_publisher.adapters.notice_publisher_abc import NoticePublisherABC


class NoticePublishBuilder:
    def __init__(self, notice: Union[Notice, str], notice_repository: NoticeRepositoryABC,
                 notice_publisher: NoticePublisherABC, remote_path: str = None):
        self.notice_repository = notice_repository
        if isinstance(notice, str):
            notice_id = notice
            notice: Notice = self.notice_repository.get(reference=notice_id)
            if notice is None:
                raise Exception(f"Notice {notice_id} could not be found.")

        self.notice = notice
        self.check_publish_eligibility()

        self.notice_publisher = notice_publisher
        self.remote_path = remote_path

    def check_publish_eligibility(self):
        if self.notice.status != NoticeStatus.ELIGIBLE_FOR_PUBLISHING:
            raise UnsupportedStatusTransition(
                f"Notice {self.notice.ted_id} is not Eligible for Publishing. Status: {self.notice.status}")

    def package_content(self) -> bytes:
        mets_manifestation = self.notice.mets_manifestation
        if not mets_manifestation or not mets_manifestation.object_data:
            raise ValueError("Notice does not have a METS manifestation to be published.")

        package_content = base64.b64decode(bytes(mets_manifestation.object_data, encoding='utf-8'), validate=True)
        return package_content

    def build_remote_path(self) -> str:
        remote_path = self.remote_path
        if remote_path is None:
            remote_path = f"{config.SFTP_PATH}/{self.notice.ted_id}"
            if ARCHIVE_DEFAULT_FORMAT == "zip":
                remote_path += '.zip'
        return remote_path

    def publish(self):
        source_file = tempfile.NamedTemporaryFile()
        source_file.write(self.package_content())

        try:
            if self.notice_publisher.publish(source_path=Path(source_file.name), remote_path=self.build_remote_path()):
                self.notice.update_status_to(NoticeStatus.PUBLISHED)
                self.notice_repository.update(self.notice)
        except Exception as e:
            raise Exception(f"Notice {self.notice.ted_id} could not be published: " + str(e))

        return self.notice.status == NoticeStatus.PUBLISHED


def publish_notice(notice: Union[Notice, str], notice_publisher: NoticePublisherABC,
                   notice_repository: NoticeRepositoryABC, remote_path=None) -> bool:
    publish_builder = NoticePublishBuilder(notice, notice_repository, notice_publisher, remote_path)
    return publish_builder.publish()


def publish_single_notice(notice: Union[Notice, str], notice_repository: NoticeRepositoryABC, hostname, username,
                          password, port=None, remote_path=None) -> bool:
    notice_publisher: NoticePublisherABC = NoticePublisherFactory.get_publisher(hostname=hostname, username=username,
                                                                                password=password, port=port,
                                                                                remote_path=remote_path)
    notice_publisher.connect()
    notice_published: bool = publish_notice(notice, notice_publisher, notice_repository, remote_path)
    notice_publisher.disconnect()

    return notice_published
