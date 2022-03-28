import pytest

from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.core.model.metadata import TEDMetadata
from ted_sws.core.model.notice import Notice

NOTICE_TED_ID = "123456"
TEST_DATABASE_NAME = "test_database_name"


def test_notice_repository_create(mongodb_client):
    mongodb_client.drop_database(TEST_DATABASE_NAME)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client, database_name=TEST_DATABASE_NAME)
    notice = Notice(ted_id=NOTICE_TED_ID, original_metadata=TEDMetadata(**{"AA": "Metadata"}),
                    xml_manifestation=XMLManifestation(object_data="HELLO"))
    notice_repository.add(notice)
    result_notice = notice_repository.get(reference=NOTICE_TED_ID)
    assert result_notice
    assert result_notice.ted_id == NOTICE_TED_ID
    assert result_notice.original_metadata.AA == "Metadata"
    result_notices = list(notice_repository.list())
    assert result_notices
    assert len(result_notices) == 1
    notice_repository.add(notice)
    notice.original_metadata = TEDMetadata(**{"AA": "Updated metadata"})
    notice_repository.update(notice)
    result_notice = notice_repository.get(reference=NOTICE_TED_ID)
    assert result_notice
    assert result_notice.ted_id == NOTICE_TED_ID
    assert result_notice.original_metadata.AA == "Updated metadata"
    mongodb_client.drop_database(TEST_DATABASE_NAME)
