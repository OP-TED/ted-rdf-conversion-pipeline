#!/usr/bin/python3

# transform.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import abc
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from ted_sws.core.model import PropertyBaseModel


class MappingSuiteComponent(PropertyBaseModel, abc.ABC):
    class Config:
        validate_assignment = True


class FileResource(MappingSuiteComponent):
    """

    """
    file_name: str
    file_content: str
    original_name: Optional[str]
    parents: Optional[List[str]] = []


class NoticeFileResource(FileResource):
    """

    """
    notice_id: str



class MetadataConstraintsStandardForm(MappingSuiteComponent):
    """
    Metadata constraints structure for Standard forms
    """
    eforms_subtype: List[str]
    start_date: Optional[List[str]]
    end_date: Optional[List[str]]
    min_xsd_version: List[str]
    max_xsd_version: Optional[List[str]]


class MetadataConstraintsEform(MappingSuiteComponent):
    """
    Metadata constraints structure for eForms
    """
    eforms_subtype: List[str]
    start_date: Optional[List[str]]
    end_date: Optional[List[str]]
    eforms_sdk_versions: List[str]


class MetadataConstraints(MappingSuiteComponent):
    """
         Metadata constraints
    """
    constraints: Union[MetadataConstraintsStandardForm, MetadataConstraintsEform]


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


class MappingXPATH(MappingSuiteComponent):
    xpath: str
    form_field: Optional[str]


class MappingSuiteType(str, Enum):
    STANDARD_FORMS = "standard_forms"
    ELECTRONIC_FORMS = "eforms"

    def __str__(self):
        return self.value


class MappingSuite(MappingSuiteComponent):
    """

    """
    created_at: str = datetime.now().replace(microsecond=0).isoformat()
    identifier: str = "no_id"
    title: str = "no_title"
    version: str = "0.1.1"
    ontology_version: str = "0.0.1"
    git_latest_commit_hash: str = "no_hash"
    mapping_suite_hash_digest: str = "no_hash"
    mapping_type: Optional[MappingSuiteType] = MappingSuiteType.STANDARD_FORMS
    metadata_constraints: MetadataConstraints
    transformation_rule_set: TransformationRuleSet
    shacl_test_suites: List[SHACLTestSuite]
    sparql_test_suites: List[SPARQLTestSuite]
    transformation_test_data: TransformationTestData

    def get_mongodb_id(self) -> str:
        return f"{self.identifier}_v{self.version}"
