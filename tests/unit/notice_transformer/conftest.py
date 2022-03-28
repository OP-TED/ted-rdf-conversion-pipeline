import pytest

from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.domain.model.transform import MappingSuite
from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapperABC
from tests import TEST_DATA_PATH
from tests.fakes.fake_rml_mapper import FakeRMLMapper


@pytest.fixture
def fake_rml_mapper() -> RMLMapperABC:
    return FakeRMLMapper()


@pytest.fixture
def fake_mapping_suite() -> MappingSuite:
    repository_path = TEST_DATA_PATH / "notice_transformer"
    mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=repository_path)
    return mapping_suite_repository.get(reference="test_package")
