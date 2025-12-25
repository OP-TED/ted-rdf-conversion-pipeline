import base64

import mongomock
import pymongo
import pytest

from src.ted_sws import config
from src.ted_sws.core.model.manifestation import METSManifestation, RDFManifestation, SHACLTestSuiteValidationReport, \
    SPARQLTestSuiteValidationReport
from src.ted_sws.core.model.metadata import NormalisedMetadata, XMLMetadata
from src.ted_sws.core.model.notice import NoticeStatus, Notice
from src.ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from src.ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, TedRequestAPI
from src.ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher

NOTICE_STORAGE_FEATURES_TEST_DB = "features_test_db_for_notice"


@pytest.fixture
def mongodb_end_point():
    return config.MONGO_DB_AUTH_URL


@pytest.fixture(scope="function")
@mongomock.patch(servers=(('server.example.com', 27017),))
def mongodb_client():
    mongo_client = pymongo.MongoClient('server.example.com')
    for database_name in mongo_client.list_database_names():
        mongo_client.drop_database(database_name)
    return mongo_client


@pytest.fixture
def ted_api_end_point():
    return config.TED_API_URL


@pytest.fixture
def notice_repository(mongodb_client):
    return NoticeRepository(mongodb_client=mongodb_client, database_name=NOTICE_STORAGE_FEATURES_TEST_DB)


@pytest.fixture
def f03_notice_2020(notice_repository, ted_api_end_point):
    notice_search_query = {"query": "ND=408313-2020"}
    NoticeFetcher(notice_repository=notice_repository,
                  ted_api_adapter=TedAPIAdapter(request_api=TedRequestAPI(),
                                                ted_api_url=ted_api_end_point)).fetch_notices_by_query(
        query=notice_search_query)
    notice = notice_repository.get(reference="408313-2020")
    notice.set_xml_metadata(xml_metadata=XMLMetadata(unique_xpaths=["FAKE_INDEX_XPATHS"]))
    return notice

@pytest.fixture
def eForm_notice_2023(notice_repository, ted_api_end_point):
    notice_search_query = {"query": "ND=17554-2024"}
    NoticeFetcher(notice_repository=notice_repository,
                  ted_api_adapter=TedAPIAdapter(request_api=TedRequestAPI(),
                                                ted_api_url=ted_api_end_point)).fetch_notices_by_query(
        query=notice_search_query)
    notice = notice_repository.get(reference="17554-2024")
    notice.set_xml_metadata(xml_metadata=XMLMetadata(unique_xpaths=["FAKE_INDEX_XPATHS"]))
    return notice

@pytest.fixture
def f18_notice_2022(notice_repository, ted_api_end_point):
    notice_search_query = {"query": "ND=67623-2022"}
    NoticeFetcher(notice_repository=notice_repository,
                  ted_api_adapter=TedAPIAdapter(request_api=TedRequestAPI(),
                                                ted_api_url=ted_api_end_point)).fetch_notices_by_query(
        query=notice_search_query)
    notice = notice_repository.get(reference="67623-2022")
    notice.set_xml_metadata(xml_metadata=XMLMetadata(unique_xpaths=["FAKE_INDEX_XPATHS"]))
    return notice


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
                                                        mapping_package_identifier="mapping_package_id",
                                                        validation_results="")
    shacl_validation = SHACLTestSuiteValidationReport(object_data="This is validation report!",
                                                      test_suite_identifier="shacl_test_id",
                                                      mapping_package_identifier="mapping_package_id",
                                                      validation_results="")
    notice = Notice(ted_id=ted_id)
    notice.set_xml_manifestation(xml_manifestation)
    notice.set_original_metadata(original_metadata)
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


@pytest.fixture
def mets_package_published_name():
    return "test_package.zip"


@pytest.fixture(scope="function")
def publish_eligible_notice(publicly_available_notice, mets_package_published_name) -> Notice:
    notice = publicly_available_notice
    notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_PUBLISHING)
    notice._mets_manifestation = METSManifestation(
        object_data=base64.b64encode("METS manifestation content".encode("utf-8")),
        package_name=mets_package_published_name
    )
    return notice