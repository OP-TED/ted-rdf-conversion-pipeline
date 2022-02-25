import pytest

from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.domain.model.manifestation import XMLManifestation
from ted_sws.domain.model.metadata import TEDMetadata
from ted_sws.domain.model.notice import Notice

NOTICE_TED_ID = "123456"
TEST_DB_NAME = 'test_db'


def test_notice_repository_create(mongodb_client):
    mongodb_client.drop_database(TEST_DB_NAME)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client, database_name=TEST_DB_NAME)
    notice = Notice(ted_id=NOTICE_TED_ID, original_metadata=TEDMetadata(**{"AA": "HEY HEY"}),
                    xml_manifestation=XMLManifestation(object_data="HELLO"))
    notice_repository.add(notice)
    result_notice = notice_repository.get(reference=NOTICE_TED_ID)
    assert result_notice
    assert result_notice.ted_id == NOTICE_TED_ID
    result_notices = notice_repository.list()
    assert result_notices
    assert len(result_notices) == 1
    with pytest.raises(Exception):
        notice_repository.add(notice)
    mongodb_client.drop_database(TEST_DB_NAME)

