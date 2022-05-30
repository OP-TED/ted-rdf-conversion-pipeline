import pytest

from ted_sws import config
from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapper, SerializationFormat, DEFAULT_SERIALIZATION_FORMAT
from tests.test_data.notice_transformer import RML_MAPPER_TEST_RDF_RESULT


def test_rml_mapper(rml_test_package_path):
    rml_mapper = RMLMapper(rml_mapper_path=config.RML_MAPPER_PATH, serialization_format=DEFAULT_SERIALIZATION_FORMAT)
    rdf_result = rml_mapper.execute(package_path=rml_test_package_path)
    assert RML_MAPPER_TEST_RDF_RESULT in rdf_result

    serialization_format = SerializationFormat.TURTLE
    rml_mapper.set_serialization_format(serialization_format)
    assert rml_mapper.get_serialization_format_value() == serialization_format.value


def test_rml_mapper_with_non_existing_package(rml_non_existing_test_package_path):
    with pytest.raises(Exception):
        rml_mapper = RMLMapper(rml_mapper_path=config.RML_MAPPER_PATH, serialization_format=DEFAULT_SERIALIZATION_FORMAT)
        rml_mapper.execute(package_path=rml_non_existing_test_package_path)
