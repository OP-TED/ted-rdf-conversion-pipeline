from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.core.model.manifestation import XMLManifestation, RDFManifestation
from ted_sws.core.model.metadata import TEDMetadata
from ted_sws.core.model.notice import Notice, NoticeStatus
from mongomock.gridfs import enable_gridfs_integration

enable_gridfs_integration()

NOTICE_TED_ID = "123456"


def test_notice_repository_create(mongodb_client, aggregates_database_name):
    mongodb_client.drop_database(aggregates_database_name)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice = Notice(ted_id=NOTICE_TED_ID)
    notice.set_xml_manifestation(XMLManifestation(object_data="HELLO"))
    notice.set_original_metadata(TEDMetadata(**{"RN": NOTICE_TED_ID}))
    notice_repository.add(notice)
    result_notice = notice_repository.get(reference=NOTICE_TED_ID)
    assert result_notice
    assert result_notice.ted_id == NOTICE_TED_ID
    assert result_notice.original_metadata.RN == NOTICE_TED_ID
    result_notices = list(notice_repository.list())
    assert result_notices
    assert len(result_notices) == 1
    notice_repository.add(notice)
    notice.set_original_metadata(ted_metadata=TEDMetadata(**{"RN": ["Updated metadata"]}))
    notice_repository.update(notice)
    result_notice = notice_repository.get(reference=NOTICE_TED_ID)
    assert result_notice
    assert result_notice.ted_id == NOTICE_TED_ID
    assert result_notice.original_metadata.RN == ["Updated metadata"]
    mongodb_client.drop_database(aggregates_database_name)


def test_notice_repository_get_notice_by_status(mongodb_client, aggregates_database_name):
    mongodb_client.drop_database(aggregates_database_name)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice = Notice(ted_id=NOTICE_TED_ID)
    notice.set_xml_manifestation(XMLManifestation(object_data="HELLO"))
    notice.set_original_metadata(TEDMetadata(**{"AA": ["Metadata"]}))
    notice_repository.add(notice)
    result_notices = notice_repository.get_notices_by_status(notice_status=NoticeStatus.RAW)
    for result_notice in result_notices:
        assert result_notice.status == NoticeStatus.RAW


def test_notice_repository_default_database_name(mongodb_client, aggregates_database_name):
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    assert notice_repository._database_name == aggregates_database_name


def test_notice_repository_create_notice_from_repository_result(mongodb_client):
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice = Notice(ted_id=NOTICE_TED_ID)
    notice.set_xml_manifestation(XMLManifestation(object_data="HELLO"))
    notice.set_original_metadata(TEDMetadata(**{"AA": ["Metadata"]}))
    notice_repository.add(notice)
    result_dict = notice_repository.collection.find_one({"ted_id": notice.ted_id})
    result_notice = notice_repository._create_notice_from_repository_result(notice_dict=result_dict)
    invalid_result_notice = notice_repository._create_notice_from_repository_result(None)
    assert result_notice
    assert invalid_result_notice is None


def test_notice_repository_grid_fs(notice_2016, mongodb_client):
    file_content = "File content"
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice_2016._rdf_manifestation = RDFManifestation(object_data=file_content)
    notice_repository.add(notice=notice_2016)
    result_notice = notice_repository.get(reference=notice_2016.ted_id)
    assert result_notice.rdf_manifestation.object_data == file_content
