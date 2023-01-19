from ted_sws.core.model.notice import NoticeStatus
from ted_sws.notice_validator.services.check_availability_of_notice_in_cellar import \
    check_availability_of_notice_in_cellar, validate_notice_availability_in_cellar, \
    check_availability_of_notices_in_cellar, DEFAULT_NOTICES_BATCH_SIZE, generate_notice_uri_from_notice, \
    INVALID_NOTICE_URI


def test_generate_notice_uri_from_notice(fake_notice_F03):
    notice_uri = generate_notice_uri_from_notice(notice=fake_notice_F03)
    assert notice_uri != INVALID_NOTICE_URI


def test_validate_notices_availability_in_cellar(valid_cellar_uri, invalid_cellar_uri):
    notice_uries = [valid_cellar_uri] * DEFAULT_NOTICES_BATCH_SIZE + [invalid_cellar_uri]
    available_uries = check_availability_of_notices_in_cellar(notice_uries=notice_uries)
    assert valid_cellar_uri in available_uries
    assert invalid_cellar_uri not in available_uries

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
