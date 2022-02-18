import deepdiff
import pytest

from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.domain.model.manifestation import XMLManifestation
from ted_sws.domain.model.metadata import TEDMetadata
from ted_sws.domain.model.notice import Notice

NOTICE_TED_ID = "123456"


def test_notice_repository_create(mongodb_client):
    mongodb_client.drop_database(NoticeRepository._database_name)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice = Notice(ted_id=NOTICE_TED_ID, original_metadata=TEDMetadata(**{"AA": "HEY HEY"}),
                    xml_manifestation=XMLManifestation(object_data="HELLO"))
    notice_repository.add(notice)
    collection = notice_repository.collection
    notice_result = collection.find_one({"ted_id": NOTICE_TED_ID})
    new_notice = Notice(**notice_result)
    assert notice_result
    assert deepdiff.Delta(notice.dict(),notice_result)
    with pytest.raises(Exception):
        notice_repository.add(notice)
    mongodb_client.drop_database(NoticeRepository._database_name)
