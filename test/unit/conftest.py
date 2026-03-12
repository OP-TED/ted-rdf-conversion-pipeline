import pathlib

import pytest
from src.ted_sws import config
from src.ted_sws.notice_transformer.adapters.rml_mapper import RMLMapperABC, SerializationFormat as RMLSerializationFormat
from test import TEST_DATA_PATH
from test.fakes.fake_rml_mapper import FakeRMLMapper


@pytest.fixture
def fake_rml_mapper() -> RMLMapperABC:
    rml_mapper = FakeRMLMapper()
    rml_mapper.set_serialization_format(RMLSerializationFormat.TURTLE)
    return rml_mapper


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
def package_folder_path_for_validator():
    return pathlib.Path(TEST_DATA_PATH / "package_F03_demo")


@pytest.fixture
def fake_mapping_package_id() -> str:
    return "test_package_fake"


@pytest.fixture
def invalid_mapping_package_id() -> str:
    return "test_invalid_package"


@pytest.fixture
def aggregates_database_name():
    return config.MONGO_DB_AGGREGATES_DATABASE_NAME
