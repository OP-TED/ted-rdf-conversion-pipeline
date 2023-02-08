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
def test_package_identifier_with_version():
    return "test_package_v0.1"


@pytest.fixture
def rml_modules_path():
    return TEST_DATA_PATH / "rml_modules"


@pytest.fixture
def invalid_repository_path() -> str:
    return "non_existing_dir"


@pytest.fixture
def mapping_suite_id():
    return "package_F03_demo"


@pytest.fixture
def package_folder_path_for_validator(mapping_suite_id):
    return TEST_DATA_PATH / mapping_suite_id


@pytest.fixture
def conceptual_mappings_file_path(mapping_suite_id):
    return TEST_DATA_PATH / mapping_suite_id / "transformation" / "conceptual_mappings.xlsx"


@pytest.fixture
def mapping_suite(mapping_suite_id):
    return TEST_DATA_PATH / mapping_suite_id


@pytest.fixture
def fake_mapping_suite():
    rml_modules_path = TEST_DATA_PATH / "mapping_suite_processor" / "rml_modules"
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
