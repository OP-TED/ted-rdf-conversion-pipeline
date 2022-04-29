import pytest

from ted_sws.core.model.manifestation import RDFManifestation
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.core.model.transform import FileResource, SPARQLTestSuite, MetadataConstraints, TransformationRuleSet, \
    SHACLTestSuite, TransformationTestData, MappingSuite
from tests import TEST_DATA_PATH


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
def sparql_test_suite_with_invalid_query(invalid_sparql_file):
    return SPARQLTestSuite(identifier="sparql_test_package", sparql_tests=[invalid_sparql_file])


@pytest.fixture
def dummy_mapping_suite(sparql_test_suite):
    metadata_constrains = MetadataConstraints(constraints=dict())
    file_name = "fake_title.txt"
    empty_file_resource = FileResource(file_name=file_name, file_content="no content here", original_name=file_name)
    transformation_rule_set = TransformationRuleSet(resources=[empty_file_resource],
                                                    rml_mapping_rules=[empty_file_resource]
                                                    )
    shacl_test_suite = SHACLTestSuite(identifier="fake_shacl_test_suite",
                                      shacl_tests=[empty_file_resource])
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
    notice_2020.update_status_to(new_status=NoticeStatus.DISTILLED)

    return notice_2020
