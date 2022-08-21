from pathlib import Path

import mongomock
import pymongo
import pytest

from ted_sws import config
from ted_sws.core.model.manifestation import XMLManifestation, RDFManifestation, METSManifestation, \
    SPARQLTestSuiteValidationReport, SHACLTestSuiteValidationReport
from ted_sws.core.model.metadata import TEDMetadata, NormalisedMetadata
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.core.model.transform import MappingSuite
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryMongoDB, \
    MappingSuiteRepositoryInFileSystem
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapper, SerializationFormat
from tests import TEST_DATA_PATH
from tests.fakes.fake_rml_mapper import FakeRMLMapper


@pytest.fixture
def fake_repository_path() -> Path:
    return TEST_DATA_PATH / "notice_transformer" / "test_repository"


@pytest.fixture
def mapping_suite_id() -> str:
    return "test_package"


@pytest.fixture
def mapping_suite_repository(fake_repository_path):
    return MappingSuiteRepositoryInFileSystem(repository_path=fake_repository_path)


@pytest.fixture
def mapping_suite(mapping_suite_repository, mapping_suite_id) -> MappingSuite:
    return mapping_suite_repository.get(reference=mapping_suite_id)


@pytest.fixture(scope="function")
@mongomock.patch(servers=(('server.example.com', 27017),))
def mongodb_client():
    mongo_client = pymongo.MongoClient('server.example.com')
    for database_name in mongo_client.list_database_names():
        mongo_client.drop_database(database_name)
    return mongo_client


@pytest.fixture(scope="function")
def notice_repository(mongodb_client, transformation_eligible_notice):
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice_repository.add(notice=transformation_eligible_notice)
    return notice_repository


@pytest.fixture
def rml_mapper():
    rml_mapper = FakeRMLMapper()
    rml_mapper.set_serialization_format(SerializationFormat.TURTLE)
    return rml_mapper


@pytest.fixture(scope="function")
def transformation_eligible_notice(publicly_available_notice) -> Notice:
    notice = publicly_available_notice
    notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION)
    notice.update_status_to(NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION)
    return notice
