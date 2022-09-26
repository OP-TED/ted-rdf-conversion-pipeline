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
    original_name: Optional[str]


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


class ConceptualMappingXPATH(MappingSuiteComponent):
    xpath: str
    name: Optional[str]
    standard_form_field_id: Optional[str]
    eform_bt_id: Optional[str]


class ConceptualMappingMetadata(MappingSuiteComponent):
    base_xpath: Optional[str]


class ConceptualMapping(MappingSuiteComponent):
    """

    """
    xpaths: List[ConceptualMappingXPATH] = []
    metadata: Optional[ConceptualMappingMetadata]


class MappingSuite(MappingSuiteComponent):
    """

    """
    created_at: str = datetime.now().isoformat()
    identifier: str = "no_id"
    title: str = "no_title"
    version: str = "0.1.1"
    ontology_version: str = "0.0.1"
    xsd_version: str = "no_xsd_version"
    git_latest_commit_hash: str = "no_hash"
    metadata_constraints: MetadataConstraints
    transformation_rule_set: TransformationRuleSet
    shacl_test_suites: List[SHACLTestSuite]
    sparql_test_suites: List[SPARQLTestSuite]
    transformation_test_data: TransformationTestData
    conceptual_mapping: Optional[ConceptualMapping]

    def get_mongodb_id(self) -> str:
        return f"{self.identifier}_v{self.version}"
