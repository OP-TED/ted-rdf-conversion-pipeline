from datetime import datetime

import mongomock
import pymongo
import pytest

from ted_sws.domain.model.transform import MetadataConstraints, FileResource, TransformationRuleSet, SHACLTestSuite, \
    SPARQLTestSuite, MappingSuite
from tests import TEST_DATA_PATH


@pytest.fixture
@mongomock.patch(servers=(('server.example.com', 27017),))
def mongodb_client():
    return pymongo.MongoClient('server.example.com')


@pytest.fixture
def file_system_repository_path():
    return TEST_DATA_PATH /"notice_transformer"/"test_file_system_repository"

@pytest.fixture
def fake_mapping_suite():
    metadata_constrains = MetadataConstraints(constraints=dict())
    empty_file_resource = FileResource(file_name="fake_file.txt",file_content = "fake content")
    transformation_rule_set = TransformationRuleSet(resources=[empty_file_resource],
                                                    rml_mapping_rules=[empty_file_resource]
                                                    )
    shacl_test_suite = SHACLTestSuite(shacl_tests=[empty_file_resource])
    sparql_test_suite = SPARQLTestSuite(purpose="no_purpose",
                                        sparql_tests=[empty_file_resource]
                                        )
    mapping_suite = MappingSuite(created_at=datetime.now(),
                                 metadata_constrains=metadata_constrains,
                                 transformation_rule_set=transformation_rule_set,
                                 shacl_test_suites=[shacl_test_suite],
                                 sparql_test_suites=[sparql_test_suite]
                                 )
    return mapping_suite