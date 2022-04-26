import mongomock
import pymongo
import pytest

from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.core.model.transform import MappingSuite
from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapperABC, SerializationFormat as RMLSerializationFormat
from tests import TEST_DATA_PATH
from tests.fakes.fake_rml_mapper import FakeRMLMapper
from pathlib import Path


@pytest.fixture
def fake_rml_mapper() -> RMLMapperABC:
    rml_mapper = FakeRMLMapper()
    rml_mapper.set_serialization_format(RMLSerializationFormat.TURTLE)
    return rml_mapper


@pytest.fixture
def fake_mapping_suite(fake_repository_path, fake_mapping_suite_id) -> MappingSuite:
    repository_path = fake_repository_path
    mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=repository_path)
    return mapping_suite_repository.get(reference=fake_mapping_suite_id)


@pytest.fixture
@mongomock.patch(servers=(('server.example.com', 27017),))
def mongodb_client():
    return pymongo.MongoClient('server.example.com')
