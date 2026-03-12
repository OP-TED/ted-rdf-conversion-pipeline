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
from src.ted_sws.event_manager.services.log import log_technical_warning

from mapping_suite_sdk.mapping_package_v3.models import MappingPackageV3
from mapping_suite_sdk.core.models.collection_asset import (
    TestDataCollectionAsset,
    SPARQLTestCollectionAsset,
    SHACLTestCollectionAsset,
    SHACLShapesCollectionAsset,
    TestResultCollectionAsset,
    TechnicalMappingCollectionAsset,
    VocabularyMappingCollectionAsset,
)
from mapping_suite_sdk.core.models.file_asset import (
    RMLMappingFileAsset,
    VocabularyMappingFileAsset,
    TestDataFileAsset,
    SPARQLQueryFileAsset,
    SHACLShapesFileAsset,
    SHACLShapesResultQueryFileAsset,
)
from mapping_suite_sdk.mapping_package_v3.models.mapping_package_v3_metadata_jsonld import (
    MappingPackageV3MetadataJSONLD,
)
from mapping_suite_sdk.mapping_package_v3.models.mapping_package_v3_metadata import (
    ApplicabilityConstraints,
    DateTimeInterval,
    VersionRange,
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
class MappingPackage(MappingPackageComponent, MappingPackageV3):
    """
    Extended mapping package model that inherits from an MSSDK model.

    Combines compatibility with MSSDK version 3 (Unified) while adding legacy pipeline-specific fields.

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
    metadata: Optional[MappingPackageV3MetadataJSONLD] = Field(
        default=None,
        description="Package metadata containing general information (V3 unified format)"
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
        Automatically synchronize between legacy pipeline fields and MSSDK v3 fields.

        Populates MSSDK v3 required fields from legacy fields when missing,
        or vice versa for backward compatibility.

        This ensures the model works with both old code using legacy fields
        and new code using MSSDK v3 structure.
        Prevents infinite recursion by using a private _sync_done flag.
        """
        if getattr(self, "_sync_done", False):
            return self
        setattr(self, "_sync_done", True)

        # If MSSDK v3 fields are missing but legacy fields exist, populate from legacy
        if self.metadata is None:
            self._populate_mssdk_from_legacy()

        # If legacy fields are defaults but MSSDK v3 fields exist, populate from MSSDK
        elif self.identifier == "no_id" and self.metadata is not None:
            self._populate_legacy_from_mssdk()

        return self

    def _populate_mssdk_from_legacy(self) -> None:
        """Populate MSSDK v3 required fields from legacy pipeline fields."""
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
                # Provide minimal dummy data to satisfy MSSDK v3 requirements
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
                # Provide minimal dummy data to satisfy MSSDK v3 requirements
                self.vocabulary_mapping_suite = VocabularyMappingCollectionAsset(
                    path=Path("resources"),
                    files=[
                        VocabularyMappingFileAsset(
                            path=Path("resources/vocabulary.xml"),
                            content="<dummy>vocabulary content</dummy>"
                        )
                    ]
                )

        # metadata from legacy fields (V3 format)
        if self.metadata is None:
            # Build applicability constraints for V3 format
            applicability_constraints = None
            if self.metadata_constraints:
                constraints_data = self.metadata_constraints.constraints
                # Build document_time_interval from start_date/end_date if available
                document_time_interval = None
                if constraints_data.start_date or constraints_data.end_date:
                    start_dt = None
                    end_dt = None
                    if constraints_data.start_date and constraints_data.start_date[0]:
                        try:
                            start_dt = datetime.fromisoformat(constraints_data.start_date[0])
                        except (ValueError, IndexError):
                            log_technical_warning(message=f"Ignoring invalid start_date value in metadata constraints (unable to parse  as ISO format): {constraints_data.start_date[0]}")
                    if constraints_data.end_date and constraints_data.end_date[0]:
                        try:
                            end_dt = datetime.fromisoformat(constraints_data.end_date[0])
                        except (ValueError, IndexError):
                            log_technical_warning(message=f"Ignoring invalid end_date value in metadata constraints (unable to parse  as ISO format): {constraints_data.end_date[0]}")
                    if start_dt or end_dt:
                        document_time_interval = DateTimeInterval(start=start_dt, end=end_dt)

                if isinstance(constraints_data, MetadataConstraintsStandardForm):
                    # Standard forms: use min_xsd_version as schema version list
                    version_range = VersionRange(
                        min=constraints_data.min_xsd_version[0] if constraints_data.min_xsd_version else None,
                        max=constraints_data.max_xsd_version[0] if constraints_data.max_xsd_version else None
                    )
                    applicability_constraints = ApplicabilityConstraints(
                        document_type_list=constraints_data.eforms_subtype,
                        document_time_interval=document_time_interval,
                        document_schema_version_list=constraints_data.min_xsd_version,
                        document_version_range=version_range
                    )
                else:  # MetadataConstraintsEform
                    applicability_constraints = ApplicabilityConstraints(
                        document_type_list=constraints_data.eforms_subtype,
                        document_time_interval=document_time_interval,
                        document_schema_version_list=constraints_data.eforms_sdk_versions,
                        document_version_range=None
                    )
            else:
                # Default constraints
                applicability_constraints = ApplicabilityConstraints(
                    document_type_list=["0"],
                    document_time_interval=None,
                    document_schema_version_list=["unknown"],
                    document_version_range=None
                )

            # Parse created_at string to datetime for V3 metadata
            try:
                created_at_dt = datetime.fromisoformat(self.created_at) if self.created_at else datetime.now()
            except ValueError:
                created_at_dt = datetime.now()

            self.metadata = MappingPackageV3MetadataJSONLD(
                path=Path("metadata.jsonld"),
                context="context.jsonld",
                id=self.identifier if self.identifier != "no_id" else "unknown",
                title=self.title if self.title != "no_title" else "Unknown Package",
                project_identifier=str(self.mapping_type) if self.mapping_type else "standard_forms",
                created_at=created_at_dt,
                description=f"Mapping package {self.identifier}",
                mapping_version=self.version,
                model_version=self.ontology_version,
                applicability_constraints=applicability_constraints,
                mapping_suite_hash_digest=self.mapping_suite_hash_digest if self.mapping_suite_hash_digest else "",
                input_mime_types=["application/xml"],
                mssdk_version="3.0.0"
            )

        # Populate test_suites_sparql from legacy sparql_test_suites
        if not self.test_suites_sparql and self.sparql_test_suites:
            self.test_suites_sparql = [
                SPARQLTestCollectionAsset(
                    path=Path(f"validation/sparql/{suite.identifier}"),
                    files=[
                        SPARQLQueryFileAsset(
                            path=Path(f"validation/sparql/{suite.identifier}/{test.file_name}"),
                            content=test.file_content
                        )
                        for test in suite.sparql_tests
                    ]
                )
                for suite in self.sparql_test_suites
            ]

        # Populate test_suites_shacl from legacy shacl_test_suites
        if self.test_suites_shacl is None and self.shacl_test_suites:
            shacl_collections = [
                SHACLShapesCollectionAsset(
                    path=Path(f"validation/shacl/{suite.identifier}"),
                    files=[
                        SHACLShapesFileAsset(
                            path=Path(f"validation/shacl/{suite.identifier}/{test.file_name}"),
                            content=test.file_content
                        )
                        for test in suite.shacl_tests
                    ]
                )
                for suite in self.shacl_test_suites
            ]
            if shacl_collections:
                self.test_suites_shacl = SHACLTestCollectionAsset(
                    path=Path("validation/shacl"),
                    shacl_collections=shacl_collections,
                    shacl_result_query=SHACLShapesResultQueryFileAsset(
                        path=Path("validation/shacl/shacl_result_query.rq"),
                        content="# Placeholder SHACL result query"
                    )
                )

    def _populate_legacy_from_mssdk(self) -> None:
        """Populate legacy pipeline fields from MSSDK v3 fields when needed."""
        if self.metadata:
            # Populate basic legacy fields from V3 metadata
            # Check against default values since they are truthy strings
            if self.identifier == "no_id":
                self.identifier = self.metadata.id
            if self.title == "no_title":
                self.title = self.metadata.title
            if not self.created_at:
                # V3 created_at is datetime, convert to ISO string
                self.created_at = self.metadata.created_at.isoformat() if self.metadata.created_at else ""
            if self.version == "0.1.1":
                self.version = self.metadata.mapping_version
            if self.ontology_version == "0.0.1":
                self.ontology_version = self.metadata.model_version
            if not self.mapping_suite_hash_digest:
                self.mapping_suite_hash_digest = self.metadata.mapping_suite_hash_digest
            # Map project_identifier to mapping_type
            if self.metadata.project_identifier == "eforms":
                self.mapping_type = MappingPackageType.ELECTRONIC_FORMS
            else:
                self.mapping_type = MappingPackageType.STANDARD_FORMS

            # Populate metadata_constraints from V3 applicability_constraints
            if self.metadata.applicability_constraints:
                constraints = self.metadata.applicability_constraints
                # Extract start/end dates from document_time_interval
                start_date = None
                end_date = None
                if constraints.document_time_interval:
                    if constraints.document_time_interval.start:
                        start_date = [constraints.document_time_interval.start.isoformat()]
                    if constraints.document_time_interval.end:
                        end_date = [constraints.document_time_interval.end.isoformat()]

                # Populate constraints based on mapping type (project_identifier)
                if self.metadata.project_identifier == "eforms":
                    self.metadata_constraints = MetadataConstraints(
                        constraints=MetadataConstraintsEform(
                            eforms_subtype=constraints.document_type_list,
                            start_date=start_date,
                            end_date=end_date,
                            eforms_sdk_versions=constraints.document_schema_version_list or ["0.1"]
                        )
                    )
                else:
                    # Standard forms style
                    min_xsd = constraints.document_schema_version_list or ["0.1"]
                    max_xsd = None
                    if constraints.document_version_range:
                        if constraints.document_version_range.max:
                            max_xsd = [constraints.document_version_range.max]
                    self.metadata_constraints = MetadataConstraints(
                        constraints=MetadataConstraintsStandardForm(
                            eforms_subtype=constraints.document_type_list,
                            start_date=start_date,
                            end_date=end_date,
                            min_xsd_version=min_xsd,
                            max_xsd_version=max_xsd
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

        # Populate legacy sparql_test_suites from test_suites_sparql
        if not self.sparql_test_suites and self.test_suites_sparql:
            self.sparql_test_suites = [
                SPARQLTestSuite(
                    identifier=suite.path.name if suite.path else f"sparql_suite_{idx}",
                    sparql_tests=[
                        FileResource(
                            file_name=file.path.name,
                            file_content=file.content,
                            original_name=file.path.name
                        )
                        for file in suite.files
                    ]
                )
                for idx, suite in enumerate(self.test_suites_sparql)
            ]
            # Clear MSSDK test_suites_sparql after populating
            self.test_suites_sparql = []

        # Populate legacy shacl_test_suites from test_suites_shacl
        if not self.shacl_test_suites and self.test_suites_shacl:
            self.shacl_test_suites = [
                SHACLTestSuite(
                    identifier=collection.path.name if collection.path else f"shacl_suite_{idx}",
                    shacl_tests=[
                        FileResource(
                            file_name=file.path.name,
                            file_content=file.content,
                            original_name=file.path.name
                        )
                        for file in collection.files
                    ]
                )
                for idx, collection in enumerate(self.test_suites_shacl.shacl_collections)
            ]
            # Clear MSSDK test_suites_shacl after populating
            self.test_suites_shacl = None
