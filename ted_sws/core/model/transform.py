#!/usr/bin/python3

# transform.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import abc
from datetime import datetime
from typing import List, Optional

from ted_sws.core.model import PropertyBaseModel


class MappingSuiteComponent(PropertyBaseModel, abc.ABC):
    class Config:
        validate_assignment = True


class FileResource(MappingSuiteComponent):
    """

    """
    file_name: str
    file_content: str


class MetadataConstraints(MappingSuiteComponent):
    """

    """
    constraints: dict


class TransformationRuleSet(MappingSuiteComponent):
    """

    """
    resources: List[FileResource]
    rml_mapping_rules: List[FileResource]


class SHACLTestSuite(MappingSuiteComponent):
    """

    """
    identifier: str
    shacl_tests: List[FileResource]


class SPARQLTestSuite(MappingSuiteComponent):
    """

    """
    identifier: str
    sparql_tests: List[FileResource]


class TransformationTestData(MappingSuiteComponent):
    """

    """
    test_data: List[FileResource]


class MappingSuite(MappingSuiteComponent):
    """

    """
    created_at: str = datetime.now().isoformat()
    identifier: str = "no_id"
    title: str = "no_title"
    version: str = "0.1"
    ontology_version: str = "0.0.1"
    metadata_constraints: MetadataConstraints
    transformation_rule_set: TransformationRuleSet
    shacl_test_suites: List[SHACLTestSuite]
    sparql_test_suites: List[SPARQLTestSuite]
    transformation_test_data: TransformationTestData
