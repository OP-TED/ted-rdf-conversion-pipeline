import pathlib
from typing import List

import pytest

from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.core.model.notice import Notice
from ted_sws.data_sampler.services.notice_xml_indexer import index_notice
from tests import TEST_DATA_PATH


@pytest.fixture
def notice_eligibility_repository_path():
    return TEST_DATA_PATH / "notice_transformer" / "test_repository"


@pytest.fixture
def file_system_repository_path():
    return TEST_DATA_PATH / "notice_transformer" / "mapping_suite_processor_repository"


@pytest.fixture
def notice_normalisation_test_data_path():
    return TEST_DATA_PATH / "notice_normalisation"


@pytest.fixture
def eforms_xml_notice_paths() -> List[pathlib.Path]:
    eforms_xml_notices_path = TEST_DATA_PATH / "eforms_samples"
    return list(eforms_xml_notices_path.glob("**/*.xml"))


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
