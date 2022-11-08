import pathlib
import pytest

from ted_sws import config
from tests import TEST_DATA_PATH


@pytest.fixture
def triple_store_endpoint_url() -> str:
    return config.TRIPLE_STORE_ENDPOINT_URL


@pytest.fixture
def rdf_file_path() -> pathlib.Path:
    return TEST_DATA_PATH / "rdf_manifestations" / "002705-2021.ttl"


@pytest.fixture
def rdf_content(rdf_file_path) -> str:
    return rdf_file_path.read_text(encoding="utf-8")


@pytest.fixture
def organisation_cet_uri() -> str:
    return "http://www.w3.org/ns/org#Organization"


@pytest.fixture
def procedure_cet_uri() -> str:
    return "http://data.europa.eu/a4g/ontology#Procedure"
