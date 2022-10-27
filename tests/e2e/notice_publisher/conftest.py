import pytest

from ted_sws.notice_publisher.adapters.s3_notice_publisher import S3Publisher


@pytest.fixture
def notice_s3_bucket_name():
    return "test-notice"


@pytest.fixture
def notice_rdf_s3_bucket_name():
    return "test-notice-rdf"


@pytest.fixture
def s3_publisher() -> S3Publisher:
    return S3Publisher()
