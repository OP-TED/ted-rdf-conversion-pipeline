import pathlib

import pytest

from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapperABC, SerializationFormat as RMLSerializationFormat
from tests import TEST_DATA_PATH
from tests.fakes.fake_rml_mapper import FakeRMLMapper


@pytest.fixture
def fake_rml_mapper() -> RMLMapperABC:
    rml_mapper = FakeRMLMapper()
    rml_mapper.set_serialization_format(RMLSerializationFormat.TURTLE)
    return rml_mapper


@pytest.fixture
def rdf_file_path() -> pathlib.Path:
    return TEST_DATA_PATH / "example.ttl"


@pytest.fixture
def rdf_content(rdf_file_path) -> str:
    return rdf_file_path.read_text(encoding="utf-8")


@pytest.fixture
def organisation_cet_uri() -> str:
    return "http://data.europa.eu/a4g/ontology#Organisation"
