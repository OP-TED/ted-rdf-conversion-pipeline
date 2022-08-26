import base64

import mongomock
import pymongo
import pytest

from ted_sws import config
from ted_sws.core.model.manifestation import METSManifestation
from ted_sws.core.model.notice import NoticeStatus, Notice
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository


@pytest.fixture
def sftp_remote_folder_path():
    return config.SFTP_PATH


@pytest.fixture(scope="function")
@mongomock.patch(servers=(('server.example.com', 27017),))
def mongodb_client():
    mongo_client = pymongo.MongoClient('server.example.com')
    for database_name in mongo_client.list_database_names():
        mongo_client.drop_database(database_name)
    return mongo_client


@pytest.fixture(scope="function")
def publish_eligible_notice(publicly_available_notice) -> Notice:
    notice = publicly_available_notice
    notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_PUBLISHING)
    notice._mets_manifestation = METSManifestation(
        object_data=base64.b64encode("METS manifestation content".encode("utf-8")))
    return notice


@pytest.fixture(scope="function")
def notice_repository(mongodb_client, publish_eligible_notice):
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice_repository.add(notice=publish_eligible_notice)
    return notice_repository


@pytest.fixture
def sftp_endpoint():
    return config.SFTP_HOST
