import pathlib

import pytest
from src.ted_sws import config
from src.ted_sws.core.model.manifestation import XMLManifestation
from src.ted_sws.core.model.notice import Notice
from src.ted_sws.data_manager.adapters.mapping_package_repository import MappingPackageRepositoryInFileSystem, \
    MappingPackageRepositoryMongoDB
from src.ted_sws.data_sampler.services.notice_xml_indexer import index_notice
from src.ted_sws.notice_metadata_processor.services.metadata_normalizer import normalise_notice
from test import TEST_DATA_PATH
from test.fakes.fake_repository import FakeNoticeRepository


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
def normalised_notice(notice_2020, load_mapping_suite_and_package, mapping_package, mongodb_client):
    notice = notice_2020.copy()
    notice.mapping_package_identifier = mapping_package.id
    normalise_notice(notice=notice, mongodb_client=mongodb_client)
    return notice


@pytest.fixture
def normalised_eForm_notice(indexed_eform_notice_622690, load_mapping_suite_and_package, mapping_package, mongodb_client):
    notice = indexed_eform_notice_622690.copy()
    notice.mapping_package_identifier = mapping_package.id
    normalise_notice(notice=notice, mongodb_client=mongodb_client)
    return notice


@pytest.fixture
def mapping_package_repository_with_mapping_package(notice_eligibility_repository_path):
    mapping_package_repository = MappingPackageRepositoryInFileSystem(repository_path=notice_eligibility_repository_path)
    return mapping_package_repository


@pytest.fixture
def clean_mapping_package_repository(mongodb_client):
    mapping_package_repository = MappingPackageRepositoryMongoDB(mongodb_client=mongodb_client)
    return mapping_package_repository


@pytest.fixture
def sample_ef_html_unsafe_notice_path() -> pathlib.Path:
    return TEST_DATA_PATH / "notice_normalisation" / "ef_html_unsafe_notice.xml"


@pytest.fixture
def sample_indexed_ef_html_unsafe_notice(
        sample_ef_html_unsafe_notice_path: pathlib.Path,
        load_mapping_suite_and_package,
        mapping_package) -> Notice:
    notice: Notice = Notice(ted_id=sample_ef_html_unsafe_notice_path.name)
    notice.set_xml_manifestation(
        XMLManifestation(object_data=sample_ef_html_unsafe_notice_path.read_text()))
    notice.mapping_package_identifier = mapping_package.id

    return index_notice(notice)


@pytest.fixture
def sample_sf_html_unsafe_notice_path() -> pathlib.Path:
    return TEST_DATA_PATH / "notice_normalisation" / "sf_html_unsafe_notice.xml"


@pytest.fixture
def sample_indexed_sf_html_unsafe_notice(
        sample_sf_html_unsafe_notice_path: pathlib.Path,
        load_mapping_suite_and_package,
        mapping_package) -> Notice:
    notice: Notice = Notice(ted_id=sample_sf_html_unsafe_notice_path.name)
    notice.set_xml_manifestation(
        XMLManifestation(object_data=sample_sf_html_unsafe_notice_path.read_text()))
    notice.mapping_package_identifier = mapping_package.id

    return index_notice(notice)


@pytest.fixture
def html_incompatible_str() -> str:
    """Provides a test string containing HTML incompatible characters."""
    return "Construction work & planning <br />"
