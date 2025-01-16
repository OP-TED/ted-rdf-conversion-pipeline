import json
from typing import Dict

import pytest

from ted_sws.core.model.notice import NoticeStatus, Notice
from ted_sws.notice_packager.model.metadata import PackagerMetadata
from tests import TEST_DATA_PATH


@pytest.fixture(scope="function")
def package_eligible_notice(publicly_available_notice) -> Notice:
    notice = publicly_available_notice
    notice._distilled_rdf_manifestation.object_data = (
            TEST_DATA_PATH / "notice_packager" / "templates" / "2021_S_004_003545_0.notice.rdf").read_text()
    notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_PACKAGING)
    return notice


@pytest.fixture
def template_sample_metadata_json() -> Dict:
    """Load template metadata from JSON file."""
    return json.load((TEST_DATA_PATH / "notice_packager" / "template_metadata.json").open())


@pytest.fixture
def template_sample_metadata(template_sample_metadata_json) -> PackagerMetadata:
    """Create PackagerMetadata from JSON."""
    return PackagerMetadata(**template_sample_metadata_json)

@pytest.fixture
def work_id_str() -> str:
    """Returns the work_id as str"""
    return "work_id"


@pytest.fixture
def work_id_predicate() -> str:
    """Returns the URI predicate for the CDM work identifier."""
    return "http://publications.europa.eu/ontology/cdm#work_id"