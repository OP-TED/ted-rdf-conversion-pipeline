import pytest

from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.notice_validator.services.check_availability_of_notice_in_cellar import \
    check_availability_of_notice_in_cellar, validate_notice_availability_in_cellar, \
    validate_and_update_notice_availability_in_cellar_by_id, validate_and_update_notice_availability_in_cellar


def test_check_availability_of_notice_in_cellar(valid_cellar_uri, invalid_cellar_uri):
    assert check_availability_of_notice_in_cellar(notice_uri=valid_cellar_uri)
    assert not check_availability_of_notice_in_cellar(notice_uri=invalid_cellar_uri)


def test_validate_notice_availability_in_cellar(fake_notice_F03, valid_cellar_uri, invalid_cellar_uri):
    fake_notice_F03._status = NoticeStatus.PUBLISHED
    validate_notice_availability_in_cellar(notice=fake_notice_F03)

    fake_notice_F03._status = NoticeStatus.PUBLISHED
    validate_notice_availability_in_cellar(notice=fake_notice_F03, notice_uri=valid_cellar_uri)
    assert fake_notice_F03.status == NoticeStatus.PUBLICLY_AVAILABLE

    fake_notice_F03._status = NoticeStatus.PUBLISHED
    validate_notice_availability_in_cellar(notice=fake_notice_F03, notice_uri=invalid_cellar_uri)
    assert fake_notice_F03.status == NoticeStatus.PUBLICLY_UNAVAILABLE


def test_validate_and_update_notice_availability_in_cellar_by_id(fake_mongodb_client, fake_notice_F03,
                                                                 valid_cellar_uri):
    fake_notice_F03._status = NoticeStatus.PUBLISHED

    notice_repository: NoticeRepository = NoticeRepository(mongodb_client=fake_mongodb_client)
    notice_repository.add(fake_notice_F03)

    notice = validate_and_update_notice_availability_in_cellar_by_id(notice_id=fake_notice_F03.ted_id,
                                                                     mongodb_client=fake_mongodb_client,
                                                                     notice_uri=valid_cellar_uri)
    assert notice.status == NoticeStatus.PUBLICLY_AVAILABLE

    fake_notice_F03._status = NoticeStatus.PUBLISHED
    with pytest.raises(ValueError):
        validate_and_update_notice_availability_in_cellar_by_id(notice_id="invalid_notice_id",
                                                                mongodb_client=fake_mongodb_client,
                                                                notice_uri=valid_cellar_uri)
        assert notice.status == NoticeStatus.PUBLISHED


def test_validate_and_update_notice_availability_in_cellar(fake_mongodb_client, fake_notice_F03,
                                                           valid_cellar_uri):
    fake_notice_F03._status = NoticeStatus.PUBLISHED

    notice_repository: NoticeRepository = NoticeRepository(mongodb_client=fake_mongodb_client)
    notice_repository.add(fake_notice_F03)

    db_notice_with_old_status = notice_repository.get(reference=fake_notice_F03.ted_id)
    assert db_notice_with_old_status.status == NoticeStatus.PUBLISHED

    notice = validate_and_update_notice_availability_in_cellar(notice=fake_notice_F03,
                                                               mongodb_client=fake_mongodb_client,
                                                               notice_uri=valid_cellar_uri)
    assert notice.status == NoticeStatus.PUBLICLY_AVAILABLE

    db_notice_with_new_status = notice_repository.get(reference=fake_notice_F03.ted_id)
    assert db_notice_with_new_status.status == NoticeStatus.PUBLICLY_AVAILABLE
