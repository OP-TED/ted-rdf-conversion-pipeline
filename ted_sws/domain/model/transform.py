#!/usr/bin/python3

# transform.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import abc
import datetime
from typing import List, Optional

from ted_sws.domain.model import PropertyBaseModel


class MappingSuiteComponent(PropertyBaseModel, abc.ABC):
    class Config:
        validate_assignment = True
        orm_mode = True


class FileResource(MappingSuiteComponent):
    file_name: str
    file_content: str


class MetadataConstraints(MappingSuiteComponent):
    constraints: dict


class TransformationRuleSet(MappingSuiteComponent):
    resources: List[FileResource]
    rml_mapping_rules: List[FileResource]


class SHACLTestSuite(MappingSuiteComponent):
    shacl_tests: List[FileResource]


class SPARQLTestSuite(MappingSuiteComponent):
    purpose: Optional[str]
    sparql_tests: List[FileResource]


class MappingSuite(MappingSuiteComponent):
    created: datetime.datetime
    identifier: str
    title: str
    version: str = "0.0.1"
    metadata_constrains: MetadataConstraints
    transformation_rule_set: TransformationRuleSet
    shacl_test_suites: List[SHACLTestSuite]
    sparql_test_suites: List[SPARQLTestSuite]
