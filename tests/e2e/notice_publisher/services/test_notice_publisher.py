import pytest

from ted_sws import config
from ted_sws.core.model.manifestation import METSManifestation, RDFManifestation
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.notice_publisher.adapters.s3_notice_publisher import S3Publisher
from ted_sws.notice_publisher.adapters.sftp_notice_publisher import SFTPPublisher
from ted_sws.notice_publisher.services.notice_publisher import publish_notice_by_id, publish_notice, \
    publish_notice_into_s3, publish_notice_into_s3_by_id, publish_notice_rdf_into_s3_by_id, publish_notice_rdf_into_s3, \
    publish_notice_rdf_content_into_s3
from ted_sws.notice_packager import DEFAULT_NOTICE_PACKAGE_EXTENSION
from ted_sws.notice_transformer.services.notice_transformer import DEFAULT_TRANSFORMATION_FILE_EXTENSION


def test_notice_publisher(notice_2016, fake_mongodb_client):
    notice = notice_2016
    notice_repository = NoticeRepository(mongodb_client=fake_mongodb_client)
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
    sftp_publisher.remove(f"{config.SFTP_PATH}/{notice.ted_id}{DEFAULT_NOTICE_PACKAGE_EXTENSION}")
    sftp_publisher.disconnect()
    assert not sftp_publisher.is_connected


def test_s3_notice_publisher(notice_2016, fake_mongodb_client, notice_s3_bucket_name, s3_publisher: S3Publisher,
                             notice_mets_manifestation):
    notice = notice_2016
    notice_repository = NoticeRepository(mongodb_client=fake_mongodb_client)
    notice_repository.add(notice)
    notice_id = notice.ted_id
    object_name = f"{notice_id}{DEFAULT_NOTICE_PACKAGE_EXTENSION}"

    rdf_manifestation = RDFManifestation(object_data="62f0baf9a5458a3a67761392")
    mets_manifestation = notice_mets_manifestation

    notice._status = NoticeStatus.VALIDATED
    notice.set_rdf_manifestation(rdf_manifestation)
    notice.set_distilled_rdf_manifestation(rdf_manifestation)
    notice._status = NoticeStatus.ELIGIBLE_FOR_PACKAGING
    notice.set_mets_manifestation(mets_manifestation)

    notice_repository.update(notice)

    notice._status = NoticeStatus.ELIGIBLE_FOR_PUBLISHING

    notice_repository.update(notice)

    publish_result: bool = publish_notice_into_s3_by_id(
        notice_id=notice_id,
        notice_repository=notice_repository,
        bucket_name=notice_s3_bucket_name,
        s3_publisher=s3_publisher
    )

    assert publish_result
    assert s3_publisher.is_published(bucket_name=notice_s3_bucket_name, object_name=object_name)

    with pytest.raises(ValueError):
        notice._status = NoticeStatus.ELIGIBLE_FOR_PUBLISHING
        notice._mets_manifestation = None
        publish_notice_into_s3(notice, s3_publisher=s3_publisher)

    s3_publisher.remove_object(bucket_name=notice_s3_bucket_name, object_name=object_name)
    s3_publisher.remove_bucket(bucket_name=notice_s3_bucket_name)

    assert not s3_publisher.is_published(bucket_name=notice_s3_bucket_name, object_name=object_name)


def test_s3_notice_rdf_publisher(notice_2016, fake_mongodb_client, notice_rdf_s3_bucket_name,
                                 s3_publisher: S3Publisher):
    notice = notice_2016
    notice_repository = NoticeRepository(mongodb_client=fake_mongodb_client)
    notice_repository.add(notice)
    notice_id = notice.ted_id
    object_name = f"{notice_id}{DEFAULT_TRANSFORMATION_FILE_EXTENSION}"

    rdf_manifestation = RDFManifestation(object_data="dGhpcyBpcyBhIHRlc3QgUkRG")
    notice._status = NoticeStatus.VALIDATED
    notice.set_rdf_manifestation(rdf_manifestation)
    notice.set_distilled_rdf_manifestation(rdf_manifestation)
    notice_repository.update(notice)

    publish_result: bool = publish_notice_rdf_into_s3_by_id(
        notice_id=notice_id,
        notice_repository=notice_repository,
        bucket_name=notice_rdf_s3_bucket_name,
        s3_publisher=s3_publisher
    )

    assert publish_result
    assert s3_publisher.is_published(bucket_name=notice_rdf_s3_bucket_name, object_name=object_name)

    with pytest.raises(ValueError):
        notice._rdf_manifestation = None
        publish_notice_rdf_into_s3(notice, s3_publisher=s3_publisher)

    s3_publisher.remove_object(bucket_name=notice_rdf_s3_bucket_name, object_name=object_name)
    s3_publisher.remove_bucket(bucket_name=notice_rdf_s3_bucket_name)

    assert not s3_publisher.is_published(bucket_name=notice_rdf_s3_bucket_name, object_name=object_name)

    publish_result = publish_notice_rdf_content_into_s3(
        rdf_manifestation=rdf_manifestation,
        object_name=object_name,
        bucket_name=notice_rdf_s3_bucket_name,
        s3_publisher=s3_publisher
    )

    assert publish_result
    assert s3_publisher.is_published(bucket_name=notice_rdf_s3_bucket_name, object_name=object_name)

    s3_publisher.remove_object(bucket_name=notice_rdf_s3_bucket_name, object_name=object_name)
    s3_publisher.remove_bucket(bucket_name=notice_rdf_s3_bucket_name)
