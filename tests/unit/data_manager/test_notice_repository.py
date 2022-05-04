from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.core.model.metadata import TEDMetadata
from ted_sws.core.model.notice import Notice, NoticeStatus
from mongomock.gridfs import enable_gridfs_integration
enable_gridfs_integration()


NOTICE_TED_ID = "123456"


def test_notice_repository_create(mongodb_client):
    mongodb_client.drop_database(NoticeRepository._database_name)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
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
    mongodb_client.drop_database(NoticeRepository._database_name)


def test_notice_repository_get_notice_by_status(mongodb_client):
    mongodb_client.drop_database(NoticeRepository._database_name)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice = Notice(ted_id=NOTICE_TED_ID, original_metadata=TEDMetadata(**{"AA": "Metadata"}),
                    xml_manifestation=XMLManifestation(object_data="HELLO"))
    notice_repository.add(notice)
    result_notices = notice_repository.get_notice_by_status(notice_status=NoticeStatus.RAW)
    for result_notice in result_notices:
        assert result_notice.status == NoticeStatus.RAW


def test_notice_repository_default_database_name(mongodb_client):
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    assert notice_repository._database_name == NoticeRepository._database_name

def test_notice_repository_create_notice_from_repository_result(mongodb_client):
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice = Notice(ted_id=NOTICE_TED_ID, original_metadata=TEDMetadata(**{"AA": "Metadata"}),
                    xml_manifestation=XMLManifestation(object_data="HELLO"))
    notice_repository.add(notice)
    result_dict = notice_repository.collection.find_one({"ted_id": notice.ted_id})
    result_notice = notice_repository._create_notice_from_repository_result(notice_dict=result_dict)
    invalid_result_notice = notice_repository._create_notice_from_repository_result(None)
    assert result_notice
    assert invalid_result_notice is None
