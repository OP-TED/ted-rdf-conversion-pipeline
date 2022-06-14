import pytest

from ted_sws.core.model.manifestation import RDFManifestation
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.core.model.transform import FileResource, SPARQLTestSuite, MetadataConstraints, TransformationRuleSet, \
    SHACLTestSuite, TransformationTestData, MappingSuite
from tests import TEST_DATA_PATH
from ted_sws.core.adapters.xml_preprocessor import XMLPreprocessorABC
from tests.fakes.fake_xslt_transformer import FakeXSLTTransformer

@pytest.fixture
def query_content():
    return """# title: Official name
# description: this is a description
PREFIX epo: <http://data.europa.eu/a4g/ontology#>
ASK
WHERE
{
  ?this epo:playedBy / epo:hasDefaultContactPoint / epo:hasFax ?organisationContactPointFax .
}
    """


@pytest.fixture
def query_content_without_description():
    return """

    # title : Official name

    PREFIX epo: <http://data.europa.eu/a4g/ontology#>
    ASK
    WHERE
    {
      ?this epo:playedBy / epo:hasDefaultContactPoint / epo:hasFax ?organisationContactPointFax .
    }
        """


@pytest.fixture
def query_content_with_xpath():
    return """
    # title: Official name
    #xpath: //some/xpath/goes/here
    # description: this is a description

    PREFIX epo: <http://data.europa.eu/a4g/ontology#>
    ASK
    WHERE
    {
      ?this epo:playedBy / epo:hasDefaultContactPoint / epo:hasFax ?organisationContactPointFax .
    }
        """


@pytest.fixture
def rdf_file_content():
    path = TEST_DATA_PATH / "example.ttl"
    return path.read_text()


@pytest.fixture
def shacl_file_content():
    path = TEST_DATA_PATH / "ePO_shacl_shapes.xml"
    return path.read_text()


@pytest.fixture
def shacl_file_two_content():
    path = TEST_DATA_PATH / "ePO_shacl_shapes_two.xml"
    return path.read_text()


@pytest.fixture
def list_of_shacl_files(shacl_file_content, shacl_file_two_content):
    return [
        FileResource(file_name="shacl_file_one.xml", file_content=shacl_file_content),
        FileResource(file_name="shacl_file_two.xml", file_content=shacl_file_two_content)
    ]


@pytest.fixture
def shacl_file_one(shacl_file_content):
    return FileResource(file_name="shacl_file_one.xml", file_content=shacl_file_content)


@pytest.fixture
def shacl_file_two(shacl_file_two_content):
    return FileResource(file_name="shacl_file_two.xml", file_content=shacl_file_two_content)


@pytest.fixture
def shacl_file_with_error():
    return FileResource(file_name="shacl_file_with_error", file_content="something fishy")


@pytest.fixture
def validator_query():
    return """
prefix dash: <http://datashapes.org/dash#>
prefix sh: <http://www.w3.org/ns/shacl#>
prefix message: <http://www.w3.org/ns/shacl#message>

SELECT ?focusNode ?message ?resultPath ?resultSeverity ?sourceConstraintComponent ?sourceShape ?value
WHERE {
    ?vr a sh:ValidationResult .
    ?vr sh:focusNode ?focusNode .
    OPTIONAL {
        ?vr sh:message ?message .
    }
    OPTIONAL {
        ?vr sh:resultPath ?resultPath .
    }
    OPTIONAL {
        ?vr sh:resultSeverity ?resultSeverity .
    }
    OPTIONAL {
        ?vr sh:sourceConstraintComponent ?sourceConstraintComponent .
    }
    OPTIONAL {
        ?vr sh:sourceShape ?sourceShape .
    }
    OPTIONAL {
        ?vr sh:value ?value .
    }
}
ORDER BY ?focusNode ?resultSeverity ?sourceConstraintComponent
    """


@pytest.fixture
def sparql_file_one():
    query = """# title: Title One
# description: this is a description
PREFIX epo: <http://data.europa.eu/a4g/ontology#>
ASK
WHERE
{
  ?this epo:playedBy / epo:hasDefaultContactPoint / epo:hasFax ?organisationContactPointFax .
}
    """
    return FileResource(file_name="good_file", file_content=query)


@pytest.fixture
def sparql_file_two():
    query = """# title: Title Two
# description: this is a description
PREFIX epo: <http://data.europa.eu/a4g/ontology#>
ASK
WHERE
{
  ?this epo:IsRoleOf / epo:hasName ?value .
}
    """
    return FileResource(file_name="better_file", file_content=query)


@pytest.fixture
def invalid_sparql_file():
    query = """# title: Title Two
# description: this is a description
ASK
WHERE
{
  ?this hasName ?value .
}
    """
    return FileResource(file_name="some_file", file_content=query)


@pytest.fixture
def sparql_test_suite(sparql_file_one, sparql_file_two):
    return SPARQLTestSuite(identifier="sparql_test_package", sparql_tests=[sparql_file_one, sparql_file_two])


@pytest.fixture
def shacl_test_suite(shacl_file_one, shacl_file_two):
    return SHACLTestSuite(identifier="shacl_test_package", shacl_tests=[shacl_file_one, shacl_file_two])


@pytest.fixture
def bad_shacl_test_suite(shacl_file_one, shacl_file_with_error):
    return SHACLTestSuite(identifier="bad_shacl_test_package", shacl_tests=[shacl_file_one, shacl_file_with_error])


@pytest.fixture
def sparql_test_suite_with_invalid_query(invalid_sparql_file):
    return SPARQLTestSuite(identifier="sparql_test_package", sparql_tests=[invalid_sparql_file])


@pytest.fixture
def dummy_mapping_suite(sparql_test_suite, shacl_test_suite):
    metadata_constrains = MetadataConstraints(constraints=dict())
    file_name = "fake_title.txt"
    empty_file_resource = FileResource(file_name=file_name, file_content="no content here", original_name=file_name)
    transformation_rule_set = TransformationRuleSet(resources=[empty_file_resource],
                                                    rml_mapping_rules=[empty_file_resource]
                                                    )
    shacl_test_suite = shacl_test_suite
    sparql_test_suite = sparql_test_suite
    transformation_test_data = TransformationTestData(test_data=[empty_file_resource])
    mapping_suite = MappingSuite(metadata_constraints=metadata_constrains,
                                 transformation_rule_set=transformation_rule_set,
                                 shacl_test_suites=[shacl_test_suite],
                                 sparql_test_suites=[sparql_test_suite],
                                 transformation_test_data=transformation_test_data
                                 )
    return mapping_suite


@pytest.fixture
def path_to_file_system_repository():
    return TEST_DATA_PATH / "notice_transformer" / "test_repository"


@pytest.fixture
def notice_with_distilled_status(notice_2020, rdf_file_content):
    notice_2020.update_status_to(new_status=NoticeStatus.NORMALISED_METADATA)
    notice_2020.update_status_to(new_status=NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION)
    notice_2020.update_status_to(new_status=NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION)
    notice_2020.set_rdf_manifestation(rdf_manifestation=RDFManifestation(object_data=rdf_file_content))
    notice_2020.set_distilled_rdf_manifestation(
        distilled_rdf_manifestation=RDFManifestation(object_data=rdf_file_content))
    notice_2020.update_status_to(new_status=NoticeStatus.DISTILLED)

    return notice_2020


@pytest.fixture
def fake_repository_path():
    return TEST_DATA_PATH / "notice_validator" / "test_repository"


@pytest.fixture
def fake_mapping_suite_id() -> str:
    return "test_package"


@pytest.fixture
def fake_mapping_suite_F03_id() -> str:
    return "test_package_F03"


@pytest.fixture
def invalid_mapping_suite_id() -> str:
    return "test_invalid_package"


@pytest.fixture
def fake_notice_id() -> str:
    return "notice"


@pytest.fixture
def fake_conceptual_mappings_F03_path(fake_repository_path, fake_mapping_suite_F03_id) -> str:
    return str(fake_repository_path / fake_mapping_suite_F03_id / "transformation" / "conceptual_mappings.xlsx")


@pytest.fixture
def fake_notice_F03_content(fake_repository_path, fake_mapping_suite_F03_id):
    with open(fake_repository_path / fake_mapping_suite_F03_id / "test_data" / "1" / "notice.xml") as f:
        notice_content = f.read()
    return notice_content


@pytest.fixture
def fake_xslt_transformer() -> XMLPreprocessorABC:
    return FakeXSLTTransformer()
