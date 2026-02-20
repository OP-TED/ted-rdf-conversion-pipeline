#!/usr/bin/python3

# transform.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

import abc
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union

from pydantic import field_validator, ConfigDict, Field, model_validator

from src.ted_sws.core.model import PropertyBaseModel

from mapping_suite_sdk.mapping_package_v2.models import MappingPackageV2
from mapping_suite_sdk.core.models.collection_asset import (
    TestDataCollectionAsset,
    SPARQLTestCollectionAsset,
    SHACLTestCollectionAsset,
    TestResultCollectionAsset,
    TechnicalMappingCollectionAsset,
    VocabularyMappingCollectionAsset,
)
from mapping_suite_sdk.core.models.file_asset import (
    RMLMappingFileAsset,
    VocabularyMappingFileAsset,
    TestDataFileAsset,
)
from mapping_suite_sdk.mapping_package_v2.models.mapping_package_v2_metadata import (
    MappingPackageV2Metadata,
    MappingPackageV2Constraints,
    MappingPackageV2EligibilityConstraints,
)

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

    # Override MSSDK v2 required fields to make them optional (will be auto-populated)
    # this is mostly a transitional solution for tests; packages are loaded and validated with pure MSSDK models first
    technical_mapping_suite: Optional[TechnicalMappingCollectionAsset] = Field(
        default=None,
        description="RML mapping files containing the technical mapping rules/definitions"
    )
    vocabulary_mapping_suite: Optional[VocabularyMappingCollectionAsset] = Field(
        default=None,
        description="Vocabulary resources used by mapping rules in XML, JSON or CSV format"
    )
    metadata: Optional[MappingPackageV2Metadata] = Field(
        default=None,
        description="Package metadata containing general information"
    )

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
    test_suites_sparql: List[SPARQLTestCollectionAsset] = Field(
        default_factory=list,
        description="Collections of SPARQL-based test suites"
    )
    test_suites_shacl: Optional[SHACLTestCollectionAsset] = Field(
        default=None,
        description="Collections of SHACL-based validation test suites"
    )

    @model_validator(mode='after')
    def sync_legacy_and_mssdk_fields(self) -> 'MappingPackage':
        """
        Automatically synchronize between legacy pipeline fields and MSSDK v2 fields.

        Populates MSSDK v2 required fields from legacy fields when missing,
        or vice versa for backward compatibility.

        This ensures the model works with both old code using legacy fields
        and new code using MSSDK v2 structure.
        Prevents infinite recursion by using a private _sync_done flag.
        """
        if getattr(self, "_sync_done", False):
            return self
        setattr(self, "_sync_done", True)

        # If MSSDK v2 fields are missing but legacy fields exist, populate from legacy
        # FIXME: this is a transitional solution for code where the legacy file system package parsing is done
        if self.metadata is None:
            self._populate_mssdk_from_legacy()

        # If legacy fields are defaults but MSSDK v2 fields exist, populate from MSSDK
        elif self.identifier == "no_id" and self.metadata is not None:
            self._populate_legacy_from_mssdk()

        return self

    def _populate_mssdk_from_legacy(self) -> None:
        """Populate MSSDK v2 required fields from legacy pipeline fields."""
        # technical_mapping_suite from transformation_rule_set
        if self.technical_mapping_suite is None:
            if self.transformation_rule_set and self.transformation_rule_set.rml_mapping_rules:
                self.technical_mapping_suite = TechnicalMappingCollectionAsset(
                    path=Path("transformation/mappings"),
                    files=[
                        RMLMappingFileAsset(
                            path=Path(f"transformation/mappings/{rule.file_name}"),
                            content=rule.file_content
                        )
                        for rule in self.transformation_rule_set.rml_mapping_rules
                    ]
                )
            else:
                # Provide minimal dummy data to satisfy MSSDK v2 requirements
                self.technical_mapping_suite = TechnicalMappingCollectionAsset(
                    path=Path("transformation/mappings"),
                    files=[
                        RMLMappingFileAsset(
                            path=Path("transformation/mappings/mapping.rml.ttl"),
                            content="# Placeholder RML mapping"
                        )
                    ]
                )

        # vocabulary_mapping_suite from transformation_rule_set.resources
        if self.vocabulary_mapping_suite is None:
            if self.transformation_rule_set and self.transformation_rule_set.resources:
                self.vocabulary_mapping_suite = VocabularyMappingCollectionAsset(
                    path=Path("resources"),
                    files=[
                        VocabularyMappingFileAsset(
                            path=Path(f"resources/{res.file_name}"),
                            content=res.file_content
                        )
                        for res in self.transformation_rule_set.resources
                    ]
                )
            else:
                # Provide minimal dummy data to satisfy MSSDK v2 requirements
                self.vocabulary_mapping_suite = VocabularyMappingCollectionAsset(
                    path=Path("resources"),
                    files=[
                        VocabularyMappingFileAsset(
                            path=Path("resources/vocabulary.xml"),
                            content="<dummy>vocabulary content</dummy>"
                        )
                    ]
                )

        # metadata from legacy fields
        if self.metadata is None:
            # Extract constraints for eligibility
            if self.metadata_constraints:
                constraints_data = self.metadata_constraints.constraints
                if isinstance(constraints_data, MetadataConstraintsStandardForm):
                    eligibility_constraints = MappingPackageV2EligibilityConstraints(
                        constraints=MappingPackageV2Constraints(
                            eforms_subtype=constraints_data.eforms_subtype,
                            start_date=constraints_data.start_date,
                            end_date=constraints_data.end_date,
                            eforms_sdk_versions=constraints_data.min_xsd_version  # Map min_xsd to sdk_versions
                        )
                    )
                else:  # MetadataConstraintsEform
                    eligibility_constraints = MappingPackageV2EligibilityConstraints(
                        constraints=MappingPackageV2Constraints(
                            eforms_subtype=constraints_data.eforms_subtype,
                            start_date=constraints_data.start_date,
                            end_date=constraints_data.end_date,
                            eforms_sdk_versions=constraints_data.eforms_sdk_versions
                        )
                    )
            else:
                # Default constraints
                eligibility_constraints = MappingPackageV2EligibilityConstraints(
                    constraints=MappingPackageV2Constraints(
                        eforms_subtype=["0"],
                        start_date=None,
                        end_date=None,
                        eforms_sdk_versions=["unknown"]
                    )
                )

            self.metadata = MappingPackageV2Metadata(
                path=Path("metadata.json"),
                identifier=self.identifier if self.identifier else "unknown",
                title=self.title if self.title else "Unknown Package",
                issue_date=self.created_at,
                description=f"Mapping package {self.identifier}",
                mapping_version=self.version,
                ontology_version=self.ontology_version,
                type=str(self.mapping_type) if self.mapping_type else "standard_forms",
                eligibility_constraints=eligibility_constraints,
                signature=self.mapping_suite_hash_digest if self.mapping_suite_hash_digest else ""
            )

    def _populate_legacy_from_mssdk(self) -> None:
        """Populate legacy pipeline fields from MSSDK v2 fields when needed."""
        if self.metadata:
            # Populate basic legacy fields from metadata
            # Check against default values since they are truthy strings
            if self.identifier == "no_id":
                self.identifier = self.metadata.identifier
            if self.title == "no_title":
                self.title = self.metadata.title
            if not self.created_at:
                self.created_at = self.metadata.issue_date
            if self.version == "0.1.1":
                self.version = self.metadata.mapping_version
            if self.ontology_version == "0.0.1":
                self.ontology_version = self.metadata.ontology_version
            if not self.mapping_suite_hash_digest:
                self.mapping_suite_hash_digest = self.metadata.signature
            self.mapping_type = (
                MappingPackageType.ELECTRONIC_FORMS
                if self.metadata.type == "eforms"
                else MappingPackageType.STANDARD_FORMS
            )

            # Populate metadata_constraints from eligibility_constraints
            constraints = self.metadata.eligibility_constraints.constraints
            if self.metadata.type == "eforms":
                self.metadata_constraints = MetadataConstraints(
                    constraints=MetadataConstraintsEform(
                        eforms_subtype=constraints.eforms_subtype,
                        start_date=constraints.start_date,
                        end_date=constraints.end_date,
                        eforms_sdk_versions=constraints.eforms_sdk_versions
                    )
                )
            else:
                self.metadata_constraints = MetadataConstraints(
                    constraints=MetadataConstraintsStandardForm(
                        eforms_subtype=constraints.eforms_subtype,
                        start_date=constraints.start_date,
                        end_date=constraints.end_date,
                        min_xsd_version=constraints.eforms_sdk_versions,
                        max_xsd_version=None
                    )
                )

        # Populate transformation_rule_set from MSSDK v2 suites
        if not self.transformation_rule_set or not self.transformation_rule_set.rml_mapping_rules:
            if self.technical_mapping_suite:
                rml_rules = [
                    FileResource(
                        file_name=file.path.name,
                        file_content=file.content,
                        original_name=file.path.name
                    )
                    for file in self.technical_mapping_suite.files
                ]
            else:
                rml_rules = []

            if self.vocabulary_mapping_suite:
                resources = [
                    FileResource(
                        file_name=file.path.name,
                        file_content=file.content,
                        original_name=file.path.name
                    )
                    for file in self.vocabulary_mapping_suite.files
                ]
            else:
                resources = []

            self.transformation_rule_set = TransformationRuleSet(
                resources=resources,
                rml_mapping_rules=rml_rules
            )
            # Clear MSSDK v2 technical and vocabulary suites after populating
            self.technical_mapping_suite = None
            self.vocabulary_mapping_suite = None

        # Populate transformation_test_data from test_data_suites
        if (self.transformation_test_data is None or not getattr(self.transformation_test_data, 'test_data', None)) and self.test_data_suites:
            all_files = []
            for suite in self.test_data_suites:
                all_files.extend([
                    FileResource(
                        file_name=file.path.name,
                        file_content=file.content,
                        original_name=file.path.name
                    ) for file in suite.files if isinstance(file, TestDataFileAsset)
                ])
            self.transformation_test_data = TransformationTestData(
                test_data=all_files
            )
            # Clear MSSDK v2 test_data_suites after populating
            self.test_data_suites = []
