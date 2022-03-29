from ted_sws import config
from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapper
from tests.test_data.notice_transformer import RML_MAPPER_TEST_RDF_RESULT


def test_rml_mapper(rml_test_package_path):
    rml_mapper = RMLMapper(rml_mapper_path=config.RML_MAPPER_PATH)
    rdf_result = rml_mapper.execute(package_path=rml_test_package_path)
    assert rdf_result == RML_MAPPER_TEST_RDF_RESULT