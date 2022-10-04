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


class MappingSuiteMetadataConstraintsObject(MappingSuiteComponent):
    """
    This class contains Mapping Suite Metadata Constraints Object model structure
    """
    eforms_subtype: List[int]
    start_date: List[str]
    end_date: List[str]
    min_xsd_version: List[str]
    max_xsd_version: List[str]


class MetadataConstraints(MappingSuiteComponent):
    """

    """
    constraints: MappingSuiteMetadataConstraintsObject


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
    form_field: Optional[str]


class ConceptualMappingMetadataConstraints(PropertyBaseModel):
    """
    This class contains Mapping Suite Conceptual Mapping Metadata Constraints Object model structure
    """
    eforms_subtype: Optional[List[str]]
    start_date: Optional[str]
    end_date: Optional[str]
    min_xsd_version: Optional[str]
    max_xsd_version: Optional[str]


class ConceptualMappingMetadata(MappingSuiteComponent):
    """

    """
    identifier: Optional[str]
    title: Optional[str]
    description: Optional[str]
    mapping_version: Optional[str]
    epo_version: Optional[str]
    base_xpath: Optional[str]
    metadata_constraints: Optional[ConceptualMappingMetadataConstraints]


class ConceptualMappingRule(MappingSuiteComponent):
    """

    """
    standard_form_field_id: str
    standard_form_field_name: str
    eform_bt_id: str
    eform_bt_name: str
    field_xpath: List[str]
    field_xpath_condition: List[str]
    class_path: List[str]
    property_path: List[str]
    triple_fingerprint: List[str]
    fragment_fingerprint: List[str]


class ConceptualMappingResource(MappingSuiteComponent):
    """

    """
    file_name: str


class ConceptualMappingRMLModule(MappingSuiteComponent):
    """

    """
    file_name: str


class ConceptualMapping(MappingSuiteComponent):
    """

    """
    xpaths: List[ConceptualMappingXPATH] = []
    metadata: Optional[ConceptualMappingMetadata]
    rules: List[ConceptualMappingRule] = []
    resources: List[ConceptualMappingResource] = []
    rml_modules: List[ConceptualMappingRMLModule] = []


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
