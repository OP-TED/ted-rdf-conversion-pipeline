import mongomock
import pymongo
import pytest

from ted_sws.core.model.transform import MetadataConstraints, FileResource, TransformationRuleSet, SHACLTestSuite, \
    SPARQLTestSuite, MappingSuite, TransformationTestData
from tests import TEST_DATA_PATH


@pytest.fixture
def file_system_repository_path():
    return TEST_DATA_PATH / "notice_transformer" / "mapping_suite_processor_repository"


@pytest.fixture
def rml_modules_path():
    return TEST_DATA_PATH / "rml_modules"


@pytest.fixture
@mongomock.patch(servers=(('server.example.com', 27017),))
def mongodb_client():
    return pymongo.MongoClient('server.example.com')


@pytest.fixture
def fake_mapping_suite_id() -> str:
    return "test_package_fake"


@pytest.fixture
def invalid_mapping_suite_id() -> str:
    return "test_invalid_package"


@pytest.fixture
def invalid_repository_path() -> str:
    return "non_existing_dir"


@pytest.fixture
def fake_mapping_suite():
    rml_modules_path = TEST_DATA_PATH / "mapping_suite_processor" / "digest_service" / "rml_modules"
    rml_mapping_rule_files = rml_modules_path.glob("*")
    rml_mapping_rule_file_resources = []
    for rml_mapping_rule_file in rml_mapping_rule_files:
        rml_mapping_rule_file_resources.append(
            FileResource(file_name=rml_mapping_rule_file.name, file_content=rml_mapping_rule_file.open().read(),
                         original_name=rml_mapping_rule_file.name))

    metadata_constrains = MetadataConstraints(constraints=dict())
    file_name = "fake_file.txt"
    empty_file_resource = FileResource(file_name=file_name, file_content="fake content", original_name=file_name)

    transformation_rule_set = TransformationRuleSet(resources=[empty_file_resource],
                                                    rml_mapping_rules=rml_mapping_rule_file_resources
                                                    )
    shacl_test_suite = SHACLTestSuite(identifier="fake_shacl_test_suite",
                                      shacl_tests=[empty_file_resource])
    sparql_test_suite = SPARQLTestSuite(identifier="fake_sparql_test_suite",
                                        sparql_tests=[empty_file_resource]
                                        )
    transformation_test_data = TransformationTestData(test_data=[empty_file_resource])
    mapping_suite = MappingSuite(metadata_constraints=metadata_constrains,
                                 transformation_rule_set=transformation_rule_set,
                                 shacl_test_suites=[shacl_test_suite],
                                 sparql_test_suites=[sparql_test_suite],
                                 transformation_test_data=transformation_test_data
                                 )
    return mapping_suite
