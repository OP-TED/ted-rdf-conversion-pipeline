import pytest

from ted_sws import config
from ted_sws.core.model.manifestation import METSManifestation, RDFManifestation
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.notice_publisher.adapters.sftp_notice_publisher import SFTPPublisher
from ted_sws.notice_publisher.services.notice_publisher import publish_notice_by_id, publish_notice


def test_notice_publisher(notice_2016, mongodb_client):
    notice = notice_2016
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice_repository.add(notice)
    notice_id = notice.ted_id

    rdf_manifestation = RDFManifestation(object_data="62f0baf9a5458a3a67761392")
    mets_manifestation = METSManifestation(object_data="62f0baf9a5458a3a67761392")

    notice._status = NoticeStatus.VALIDATED
    notice.set_rdf_manifestation(rdf_manifestation)
    notice._status = NoticeStatus.ELIGIBLE_FOR_PACKAGING
    notice.set_mets_manifestation(mets_manifestation)

    notice_repository.update(notice)

    notice._status = NoticeStatus.ELIGIBLE_FOR_PUBLISHING

    notice_repository.update(notice)
    sftp_publisher = SFTPPublisher()

    published = publish_notice_by_id(notice_id, notice_repository, publisher=sftp_publisher)

    assert published

    with pytest.raises(Exception):
        notice._status = NoticeStatus.ELIGIBLE_FOR_PUBLISHING
        publish_notice(notice, publisher=sftp_publisher,
                       remote_folder_path="/invalid_path")

    with pytest.raises(ValueError):
        notice._status = NoticeStatus.ELIGIBLE_FOR_PUBLISHING
        notice._mets_manifestation = None
        publish_notice(notice, publisher=sftp_publisher)
    sftp_publisher.connect()
    sftp_publisher.remove(f"{config.SFTP_PATH}/{notice.ted_id}.zip")
    sftp_publisher.disconnect()
    assert not sftp_publisher.is_connected
