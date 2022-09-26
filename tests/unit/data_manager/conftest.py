from datetime import date

import mongomock
import pymongo
import pytest

from ted_sws.core.model.supra_notice import DailySupraNotice
from ted_sws.core.model.transform import MetadataConstraints, FileResource, TransformationRuleSet, SHACLTestSuite, \
    SPARQLTestSuite, MappingSuite, TransformationTestData
from tests import TEST_DATA_PATH


@pytest.fixture
@mongomock.patch(servers=(('server.example.com', 27017),))
def mongodb_client():
    return pymongo.MongoClient('server.example.com')


@pytest.fixture
def file_system_repository_path():
    return TEST_DATA_PATH / "notice_transformer" / "test_file_system_repository"


@pytest.fixture
def fake_mapping_suite():
    metadata_constrains = MetadataConstraints(constraints=dict())
    file_name = "fake_file.txt"
    empty_file_resource = FileResource(file_name=file_name, file_content="fake content", original_name=file_name)
    transformation_rule_set = TransformationRuleSet(resources=[empty_file_resource],
                                                    rml_mapping_rules=[empty_file_resource]
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


@pytest.fixture
def daily_supra_notice():
    return DailySupraNotice(notice_ids=["1", "2", "3"], notice_fetched_date=date.today())


@pytest.fixture
def fake_mapping_suite_identifier_with_version(fake_mapping_suite):
    return fake_mapping_suite.get_mongodb_id()
