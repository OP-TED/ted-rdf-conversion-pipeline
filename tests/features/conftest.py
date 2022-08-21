import pymongo
import pytest

from ted_sws import config
from ted_sws.core.model.manifestation import METSManifestation, RDFManifestation, SHACLTestSuiteValidationReport, \
    SPARQLTestSuiteValidationReport
from ted_sws.core.model.metadata import NormalisedMetadata
from ted_sws.core.model.notice import NoticeStatus, Notice
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository

NOTICE_STORAGE_FEATURES_TEST_DB = "features_test_db_for_notice"


@pytest.fixture
def mongodb_end_point():
    return config.MONGO_DB_AUTH_URL


@pytest.fixture
def mongodb_client(mongodb_end_point):
    return pymongo.MongoClient(mongodb_end_point)


@pytest.fixture
def ted_api_end_point():
    return config.TED_API_URL


@pytest.fixture
def notice_repository(mongodb_client):
    return NoticeRepository(mongodb_client=mongodb_client, database_name=NOTICE_STORAGE_FEATURES_TEST_DB)


@pytest.fixture
def notice_id(notice_2020):
    return notice_2020.ted_id


@pytest.fixture
def fetched_notice_data(notice_2020):
    ted_id = notice_2020.ted_id
    original_metadata = notice_2020.original_metadata
    xml_manifestation = notice_2020.xml_manifestation
    return ted_id, original_metadata, xml_manifestation


@pytest.fixture(scope="function")
def publicly_available_notice(fetched_notice_data, normalised_metadata_dict) -> Notice:
    ted_id, original_metadata, xml_manifestation = fetched_notice_data
    sparql_validation = SPARQLTestSuiteValidationReport(object_data="This is validation report!",
                                                        test_suite_identifier="sparql_test_id",
                                                        mapping_suite_identifier="mapping_suite_id",
                                                        validation_results=[])
    shacl_validation = SHACLTestSuiteValidationReport(object_data="This is validation report!",
                                                      test_suite_identifier="shacl_test_id",
                                                      mapping_suite_identifier="mapping_suite_id",
                                                      validation_results=[])
    notice = Notice(ted_id=ted_id, original_metadata=original_metadata,
                    xml_manifestation=xml_manifestation)
    notice._rdf_manifestation = RDFManifestation(object_data="RDF manifestation content",
                                                 shacl_validations=[shacl_validation],
                                                 sparql_validations=[sparql_validation]
                                                 )
    notice._distilled_rdf_manifestation = RDFManifestation(object_data="RDF manifestation content",
                                                           shacl_validations=[shacl_validation],
                                                           sparql_validations=[sparql_validation]
                                                           )
    notice._mets_manifestation = METSManifestation(object_data="METS manifestation content")
    notice._normalised_metadata = NormalisedMetadata(**normalised_metadata_dict)
    notice._preprocessed_xml_manifestation = xml_manifestation
    notice._status = NoticeStatus.PUBLICLY_AVAILABLE
    return notice
