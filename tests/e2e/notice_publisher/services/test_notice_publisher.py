from ted_sws import config
from ted_sws.core.model.manifestation import METSManifestation, RDFManifestation
from ted_sws.core.model.notice import NoticeStatus, UnsupportedStatusTransition
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.notice_publisher.services.notice_publisher import publish_single_notice, NoticePublishBuilder
from ted_sws.notice_publisher.adapters.sftp_notice_publisher import SFTPNoticePublisher
import pytest


def test_notice_publisher(notice_2016, mongodb_client):
    notice = notice_2016
    notice.ted_id = "TEST_" + notice.ted_id
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

    with pytest.raises(UnsupportedStatusTransition):
        publish_single_notice(notice, notice_repository, config.SFTP_HOST, config.SFTP_USER, config.SFTP_PASSWORD)

    notice._status = NoticeStatus.ELIGIBLE_FOR_PUBLISHING

    notice_repository.update(notice)

    published = publish_single_notice(notice_id, notice_repository, config.SFTP_HOST, config.SFTP_USER,
                                      config.SFTP_PASSWORD)

    assert published

    with pytest.raises(Exception):
        notice._status = NoticeStatus.ELIGIBLE_FOR_PUBLISHING
        publish_single_notice(notice, notice_repository, config.SFTP_HOST, config.SFTP_USER, config.SFTP_PASSWORD,
                              remote_path="/invalid_path")

    with pytest.raises(Exception):
        notice._status = NoticeStatus.ELIGIBLE_FOR_PUBLISHING
        publish_single_notice("invalid_notice_id", notice_repository, config.SFTP_HOST, config.SFTP_USER,
                              config.SFTP_PASSWORD)

    with pytest.raises(ValueError):
        notice._status = NoticeStatus.ELIGIBLE_FOR_PUBLISHING
        notice._mets_manifestation = None
        publish_single_notice(notice, notice_repository, config.SFTP_HOST, config.SFTP_USER, config.SFTP_PASSWORD)

    notice_publisher = SFTPNoticePublisher(config.SFTP_HOST, config.SFTP_USER, config.SFTP_PASSWORD)
    notice_publisher.connect()
    publish_builder = NoticePublishBuilder(notice, notice_repository, notice_publisher)
    notice_publisher.remove(publish_builder.build_remote_path())
