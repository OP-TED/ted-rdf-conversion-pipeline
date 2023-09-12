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
    original_name: Optional[str] = None
    parents: Optional[List[str]] = []


class NoticeFileResource(FileResource):
    """

    """
    notice_id: str


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
    form_field: Optional[str] = None


class ConceptualMappingDiffMetadata(MappingSuiteComponent):
    """"""
    branches: Optional[List[str]] = None
    mapping_suite_ids: Optional[List[str]] = None
    files: Optional[List[Optional[str]]] = None
    defaults: Optional[dict] = None
    metadata: Optional[List[dict]] = None


class ConceptualMappingDiffData(MappingSuiteComponent):
    """"""
    html: Optional[str] = None
    transformed: Optional[dict] = None
    original: Optional[dict] = None


class ConceptualMappingDiff(MappingSuiteComponent):
    """"""
    created_at: str = datetime.now().isoformat()
    metadata: Optional[ConceptualMappingDiffMetadata] = None
    data: Optional[ConceptualMappingDiffData] = None


class ConceptualMappingMetadataConstraints(PropertyBaseModel):
    """
    This class contains Mapping Suite Conceptual Mapping Metadata Constraints Object model structure
    """
    eforms_subtype: Optional[List[str]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    min_xsd_version: Optional[str] = None
    max_xsd_version: Optional[str] = None


class ConceptualMappingMetadata(MappingSuiteComponent):
    """

    """
    identifier: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    mapping_version: Optional[str] = None
    epo_version: Optional[str] = None
    base_xpath: Optional[str] = None
    metadata_constraints: Optional[ConceptualMappingMetadataConstraints] = None


class ConceptualMappingRule(MappingSuiteComponent):
    """

    """
    standard_form_field_id: Optional[str] = None
    standard_form_field_name: Optional[str] = None
    eform_bt_id: Optional[str] = None
    eform_bt_name: Optional[str] = None
    field_xpath: Optional[List[str]] = None
    field_xpath_condition: Optional[List[str]] = None
    class_path: Optional[List[str]] = None
    property_path: Optional[List[str]] = None
    triple_fingerprint: Optional[List[str]] = None
    fragment_fingerprint: Optional[List[str]] = None


class ConceptualMappingResource(MappingSuiteComponent):
    """

    """
    file_name: Optional[str] = None


class ConceptualMappingRMLModule(MappingSuiteComponent):
    """

    """
    file_name: Optional[str] = None


class ConceptualMappingRemark(MappingSuiteComponent):
    """

    """
    standard_form_field_id: Optional[str] = None
    standard_form_field_name: Optional[str] = None
    field_xpath: Optional[List[str]] = None


class ConceptualMappingControlList(MappingSuiteComponent):
    """

    """
    field_value: Optional[str] = None
    mapping_reference: Optional[str] = None
    super_type: Optional[str] = None
    xml_path_fragment: Optional[str] = None


class ConceptualMapping(MappingSuiteComponent):
    """

    """
    xpaths: List[ConceptualMappingXPATH] = []
    metadata: Optional[ConceptualMappingMetadata] = None
    rules: List[ConceptualMappingRule] = []
    mapping_remarks: List[ConceptualMappingRemark] = []
    resources: List[ConceptualMappingResource] = []
    rml_modules: List[ConceptualMappingRMLModule] = []
    cl1_roles: List[ConceptualMappingControlList] = []
    cl2_organisations: List[ConceptualMappingControlList] = []


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
    metadata_constraints: MetadataConstraints
    transformation_rule_set: TransformationRuleSet
    shacl_test_suites: List[SHACLTestSuite]
    sparql_test_suites: List[SPARQLTestSuite]
    transformation_test_data: TransformationTestData
    conceptual_mapping: Optional[ConceptualMapping] = None

    def get_mongodb_id(self) -> str:
        return f"{self.identifier}_v{self.version}"
