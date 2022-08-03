import pathlib
from string import Template

import pytest

from ted_sws import config
from tests import TEST_DATA_PATH


@pytest.fixture
def triple_store_endpoint_url() -> str:
    return config.TRIPLE_STORE_ENDPOINT_URL


@pytest.fixture
def rdf_file_path() -> pathlib.Path:
    return TEST_DATA_PATH / "example.ttl"


@pytest.fixture
def rdf_content(rdf_file_path) -> str:
    return rdf_file_path.read_text(encoding="utf-8")


@pytest.fixture
def organisation_cet_uri() -> str:
    return "http://data.europa.eu/a4g/ontology#Organisation"
