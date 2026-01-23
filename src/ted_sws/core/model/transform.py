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

from pydantic import field_validator, ConfigDict, Field

from src.ted_sws.core.model import PropertyBaseModel

from mapping_suite_sdk.mapping_package_v2.models import MappingPackageV2
from mapping_suite_sdk.core.models.collection_asset import TestDataCollectionAsset, SAPRQLTestCollectionAsset, SHACLTestCollectionAsset, \
    TestResultCollectionAsset

class MappingPackageComponent(PropertyBaseModel, abc.ABC):
    model_config = ConfigDict(validate_assignment=True)


class FileResource(MappingPackageComponent):
    """Represents a file resource in a mapping package."""
    file_name: str
    file_content: str
    original_name: Optional[str] = None
    parents: List[str] = Field(default_factory=list)


class NoticeFileResource(FileResource):
    """Represents a file resource associated with a notice."""
    notice_id: str


class MetadataConstraintsStandardForm(MappingPackageComponent):
    """Metadata constraints structure for Standard forms."""
    # TODO: MSSDK must fix SF (v1) to have str in model even if data is int
    eforms_subtype: List[str]
    start_date: Optional[List[str]] = None
    end_date: Optional[List[str]] = None
    min_xsd_version: List[str]
    max_xsd_version: Optional[List[str]] = None

    @field_validator("eforms_subtype", mode="before")
    def coerce_eforms_subtype(cls, value):
        if isinstance(value, list):
            return [str(item) for item in value]
        return value


class MetadataConstraintsEform(MappingPackageComponent):
    """Metadata constraints structure for eForms."""
    eforms_subtype: List[str]
    start_date: Optional[List[str]] = None
    end_date: Optional[List[str]] = None
    eforms_sdk_versions: List[str]


class MetadataConstraints(MappingPackageComponent):
    """Metadata constraints container."""
    constraints: Union[MetadataConstraintsStandardForm, MetadataConstraintsEform]


class TransformationRuleSet(MappingPackageComponent):
    """Transformation rule set with vocabulary resources and RML mappings."""
    resources: List[FileResource]
    rml_mapping_rules: List[FileResource]


class SHACLTestSuite(MappingPackageComponent):
    """SHACL test suite."""
    identifier: str
    shacl_tests: List[FileResource]


class SPARQLTestSuite(MappingPackageComponent):
    """SPARQL test suite."""
    identifier: str
    sparql_tests: List[FileResource]


class TransformationTestData(MappingPackageComponent):
    """Transformation test data."""
    test_data: List[FileResource]


class MappingXPATH(MappingPackageComponent):
    """Mapping XPath expression."""
    xpath: str
    form_field: Optional[str] = None


class MappingPackageType(str, Enum):
    """Type of mapping package."""
    STANDARD_FORMS = "standard_forms"
    ELECTRONIC_FORMS = "eforms"

    def __str__(self):
        return self.value


# this will become a union- or composition-based class when more versions are added
class MappingPackage(MappingPackageComponent, MappingPackageV2):
    """
    Extended mapping package model that inherits from an MSSDK model.
    
    Combines compatibility with MSSDK version 2 while adding legacy pipeline-specific fields.
    
    IMPORTANT: Many legacy fields are optional with defaults to avoid conflicts with MSSDK models.
    """
    
    # Legacy pipeline-specific fields - MOSTLY OPTIONAL
    created_at: str = Field(
        default_factory=lambda: datetime.now().replace(microsecond=0).isoformat()
    )
    identifier: str = Field(default="no_id")
    title: str = Field(default="no_title")
    version: str = Field(default="0.1.1")
    ontology_version: str = Field(default="0.0.1")
    git_latest_commit_hash: str = Field(default="")
    mapping_suite_hash_digest: str = Field(default="")
    mapping_type: Optional[MappingPackageType] = Field( default=MappingPackageType.STANDARD_FORMS)
    metadata_constraints: Optional[MetadataConstraints] = Field(default=None)
    transformation_rule_set: Optional[TransformationRuleSet] = Field(default=None)
    shacl_test_suites: List[SHACLTestSuite] = Field(default_factory=list)
    sparql_test_suites: List[SPARQLTestSuite] = Field(default_factory=list)
    transformation_test_data: Optional[TransformationTestData] = Field(default=None)
    previous_version: Optional[str] = Field(default=None)

    # TODO fix to be forwarded to MSSDK, remove when implemented there
    # Override large/optional collection assets in MSSDK model
    test_results: Optional[TestResultCollectionAsset] = Field(
        default=None, 
        description="Collections of test transformation results (optional due to large storage requirements -- will cause MongoDB BSON error for 16MB limit)"
    )
    test_data_suites: List[TestDataCollectionAsset] = Field(
        default_factory=list,
        description="Collections of test data for transformation"
    )
    test_suites_sparql: List[SAPRQLTestCollectionAsset] = Field(
        default_factory=list,
        description="Collections of SPARQL-based test suites"
    )
    test_suites_shacl: Optional[SHACLTestCollectionAsset] = Field(
        default=None,
        description="Collections of SHACL-based validation test suites"
    )

    # TODO check this out and remove if not needed (see if any production package ID does not come with version)
    def get_mongodb_id(self) -> str:
        """Get MongoDB _id for this package."""
        return f"{self.id}_v{self.version}"
