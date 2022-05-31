import pytest

from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.core.model.manifestation import XMLManifestation, RDFManifestation
from ted_sws.core.model.metadata import TEDMetadata
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.notice_validator.services.shacl_test_suite_runner import validate_notice_with_shacl_suite
from ted_sws.notice_validator.services.sparql_test_suite_runner import validate_notice_with_sparql_suite

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


def test_notice_repository_grid_fs(notice_2016, mongodb_client):
    file_content = "File content"
    mongodb_client.drop_database(TEST_DATABASE_NAME)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client, database_name=TEST_DATABASE_NAME)
    notice_2016._rdf_manifestation = RDFManifestation(object_data=file_content)
    notice_repository.add(notice=notice_2016)
    result_notice = notice_repository.get(reference=notice_2016.ted_id)
    assert result_notice.rdf_manifestation.object_data == file_content


def test_notice_repository_store_validation_reports_in_grid_fs(notice_with_distilled_status, dummy_mapping_suite,
                                                               rdf_file_content, mongodb_client):
    mongodb_client.drop_database(TEST_DATABASE_NAME)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client, database_name=TEST_DATABASE_NAME)
    notice = notice_with_distilled_status
    validate_notice_with_shacl_suite(notice=notice, mapping_suite_package=dummy_mapping_suite)
    validate_notice_with_sparql_suite(notice=notice, mapping_suite_package=dummy_mapping_suite)
    notice_repository.add(notice)
    result_notice = notice_repository.get(reference=notice.ted_id)
    for validation_report, result_validation_report in zip(notice.rdf_manifestation.shacl_validations,
                                                           result_notice.rdf_manifestation.shacl_validations):
        assert validation_report.object_data == result_validation_report.object_data

    for validation_report, result_validation_report in zip(notice.rdf_manifestation.sparql_validations,
                                                           result_notice.rdf_manifestation.sparql_validations):
        assert validation_report.object_data == result_validation_report.object_data

    for validation_report, result_validation_report in zip(notice.distilled_rdf_manifestation.shacl_validations,
                                                           result_notice.distilled_rdf_manifestation.shacl_validations):
        assert validation_report.object_data == result_validation_report.object_data

    for validation_report, result_validation_report in zip(notice.distilled_rdf_manifestation.sparql_validations,
                                                           result_notice.distilled_rdf_manifestation.sparql_validations):
        assert validation_report.object_data == result_validation_report.object_data
