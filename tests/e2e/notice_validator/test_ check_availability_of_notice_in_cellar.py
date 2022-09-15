from ted_sws.notice_validator.services.check_availability_of_notice_in_cellar import \
    check_availability_of_notice_in_cellar


def test_check_availability_of_notice_in_cellar(valid_cellar_uri, invalid_cellar_uri):
    assert check_availability_of_notice_in_cellar(notice_uri=valid_cellar_uri)
    assert not check_availability_of_notice_in_cellar(notice_uri=invalid_cellar_uri)
