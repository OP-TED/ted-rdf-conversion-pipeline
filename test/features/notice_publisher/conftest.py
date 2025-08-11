import mongomock
import pymongo
import pytest

from src.ted_sws import config
from src.ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from src.ted_sws.notice_publisher.adapters.s3_notice_publisher import S3Publisher


@pytest.fixture
def sftp_remote_folder_path():
    return config.SFTP_PUBLISH_PATH


@pytest.fixture(scope="function")
@mongomock.patch(servers=(('server.example.com', 27017),))
def mongodb_client():
    mongo_client = pymongo.MongoClient('server.example.com')
    for database_name in mongo_client.list_database_names():
        mongo_client.drop_database(database_name)
    return mongo_client


@pytest.fixture(scope="function")
def notice_repository(mongodb_client, publish_eligible_notice):
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice_repository.add(notice=publish_eligible_notice)
    return notice_repository


@pytest.fixture
def sftp_endpoint():
    return config.SFTP_PUBLISH_HOST


@pytest.fixture
def s3_publisher():
    return S3Publisher()


@pytest.fixture
def s3_bucket_name():
    return "tmp-test-bucket"


@pytest.fixture
def rdf_manifestation_published_name(publish_eligible_notice):
    return f"{publish_eligible_notice.ted_id}.ttl"
