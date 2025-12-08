from typing import Optional

from pydantic import BaseModel

from ted_sws.core.model.transform import MappingSuiteType, MetadataConstraints


class EFormsPackageMetadataBase(BaseModel):
    identifier: str
    title: str
    created_at: str
    description: str
    mapping_version: str
    ontology_version: str
    mapping_type: Optional[MappingSuiteType] = MappingSuiteType.ELECTRONIC_FORMS
    metadata_constraints: MetadataConstraints

    class Config:
        use_enum_values = True
