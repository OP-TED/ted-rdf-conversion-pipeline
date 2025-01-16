import pathlib

import pytest

from ted_sws import config
from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.core.model.notice import Notice
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem, \
    MappingSuiteRepositoryMongoDB
from ted_sws.data_sampler.services.notice_xml_indexer import index_notice
from ted_sws.notice_metadata_processor.services.metadata_normalizer import normalise_notice
from tests import TEST_DATA_PATH
from tests.fakes.fake_repository import FakeNoticeRepository


@pytest.fixture
def notice_identifier():
    return "67623-2022"


@pytest.fixture
def api_end_point():
    return config.TED_API_URL


@pytest.fixture
def fake_notice_storage():
    return FakeNoticeRepository()


@pytest.fixture
def notice_eligibility_repository_path():
    return TEST_DATA_PATH / "notice_transformer" / "test_repository"


@pytest.fixture
def normalised_notice(notice_2020):
    notice = notice_2020.copy()
    normalise_notice(notice=notice)
    return notice


@pytest.fixture
def normalised_eForm_notice(indexed_eform_notice_622690):
    notice = indexed_eform_notice_622690.copy()
    normalise_notice(notice=notice)
    return notice


@pytest.fixture
def mapping_suite_repository_with_mapping_suite(notice_eligibility_repository_path):
    mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=notice_eligibility_repository_path)
    return mapping_suite_repository


@pytest.fixture
def clean_mapping_suite_repository(mongodb_client):
    mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    return mapping_suite_repository


@pytest.fixture
def sample_ef_html_unsafe_notice_path() -> pathlib.Path:
    return TEST_DATA_PATH / "notice_normalisation" / "ef_html_unsafe_notice.xml"


@pytest.fixture
def sample_indexed_ef_html_unsafe_notice(
        sample_ef_html_unsafe_notice_path: pathlib.Path) -> Notice:
    notice: Notice = Notice(ted_id=sample_ef_html_unsafe_notice_path.name)
    notice.set_xml_manifestation(
        XMLManifestation(object_data=sample_ef_html_unsafe_notice_path.read_text()))

    return index_notice(notice)


@pytest.fixture
def sample_sf_html_unsafe_notice_path() -> pathlib.Path:
    return TEST_DATA_PATH / "notice_normalisation" / "sf_html_unsafe_notice.xml"


@pytest.fixture
def sample_indexed_sf_html_unsafe_notice(
        sample_sf_html_unsafe_notice_path: pathlib.Path) -> Notice:
    notice: Notice = Notice(ted_id=sample_sf_html_unsafe_notice_path.name)
    notice.set_xml_manifestation(
        XMLManifestation(object_data=sample_sf_html_unsafe_notice_path.read_text()))

    return index_notice(notice)


@pytest.fixture
def html_incompatible_str() -> str:
    """Provides a test string containing HTML incompatible characters."""
    return "Construction work & planning <br />"
