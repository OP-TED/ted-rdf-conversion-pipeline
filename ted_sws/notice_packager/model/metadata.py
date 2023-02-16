#!/usr/bin/python3

# metadata.py
# Date:  22/02/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

"""
This model contains the metadata mapping/manipulation class to be used by Notice-Packager/Template-Generator
"""

import datetime
from typing import List, Dict, Optional

from pydantic import validator

from ted_sws.core.model.metadata import Metadata

METS_PROFILE = "http://publications.europa.eu/resource/mets/op-sip-profile_002"
METS_TYPE_CREATE = "create"
METS_TYPE_UPDATE = "update"
METS_TYPE_DELETE = "delete"
METS_ACCEPTED_TYPES = [METS_TYPE_CREATE, METS_TYPE_UPDATE, METS_TYPE_DELETE]
METS_DMD_MDTYPE = "OTHER"
METS_DMD_OTHERMDTYPE = "INSTANCE"
METS_DMD_HREF = "{work_identifier}_{revision}.mets.xml.dmd.rdf"
METS_DMD_ID = "{work_identifier}_{revision}_dmd_{dmd_idx}"
METS_TMD_ID = "{work_identifier}_{revision}_tmd_{tmd_idx}"
METS_TMD_HREF = "{work_identifier}_{revision}.tmd.rdf"
METS_TMD_MDTYPE = "OTHER"
METS_TMD_OTHERMDTYPE = "INSTANCE"
METS_FILE_ID = "{work_identifier}_{revision}_file_{file_idx}"
METS_NOTICE_FILE_HREF = "{work_identifier}_{revision}.notice.ttl"
METS_NOTICE_FILE_MIMETYPE = "text/turtle"
METS_NOTICE_FILE_CHECKSUM_TYPE = "SHA-256"

WORK_AGENT = "EURUN"
PUBLICATION_FREQUENCY = "OTHER"
CONCEPT_TYPE_DATASET = "TEST_DATA"
DATASET_KEYWORD = [
    "eProcurement",
    "notice"
]
BASE_CORPORATE_BODY = "&cellar-authority;corporate-body/"
BASE_WORK = "http://data.europa.eu/a4g/resource/"
BASE_TITLE = "eProcurement notice"

WORK_DO_NOT_INDEX = "true"
MANIFESTATION_TYPE = "rdf_epo"
DISTRIBUTION_STATUS = "COMPLETED"
MEDIA_TYPE = "RDF"
LANGUAGES = ["en"]
LANGUAGE = LANGUAGES[0]
USES_LANGUAGE = "MUL"

REVISION = "0"


def validate_mets_type(v):
    if v not in METS_ACCEPTED_TYPES:
        raise ValueError('No such METS type: %s' % v)


class NoticeMetadata(Metadata):
    """
    General notice metadata
    """
    id: Optional[str]
    number: Optional[str]


class MetsMetadata(Metadata):
    """
    General notice metadata
    """
    languages: List[str] = LANGUAGES
    revision: str = REVISION

    type: str = METS_TYPE_CREATE
    profile: str = METS_PROFILE
    createdate: str = datetime.datetime.now().isoformat()
    document_id: Optional[str]
    dmd_id: Optional[str]
    dmd_mdtype: str = METS_DMD_MDTYPE
    dmd_othermdtype: str = METS_DMD_OTHERMDTYPE
    dmd_href: Optional[str]
    tmd_id: Optional[str]
    tmd_href: Optional[str]
    tmd_mdtype: str = METS_TMD_MDTYPE
    tmd_othermdtype: str = METS_TMD_OTHERMDTYPE
    file_id: Optional[str]
    notice_file_href: Optional[str]
    notice_file_mimetype: Optional[str] = METS_NOTICE_FILE_MIMETYPE
    notice_file_checksum: Optional[str]
    notice_file_checksum_type: Optional[str] = METS_NOTICE_FILE_CHECKSUM_TYPE

    @validator('type')
    def validate_notice_action_type(cls, v):
        validate_mets_type(v)
        return v


class WorkMetadata(Metadata):
    """
        What is the minimal input necessary to produce the work metadata,
        and the rest is a bunch of constants OR generated values (e.g. date, URI, ...)
    """

    identifier: Optional[str]
    cdm_rdf_type: Optional[str]
    resource_type: Optional[str]
    uri: Optional[str] = None
    do_not_index: str = WORK_DO_NOT_INDEX
    date_document: str = datetime.datetime.now().strftime('%Y-%m-%d')
    created_by_agent: str = WORK_AGENT
    dataset_published_by_agent: str = WORK_AGENT
    datetime_transmission: str = datetime.datetime.now().isoformat()
    title: Optional[Dict[str, str]] = None
    date_creation: Optional[str] = datetime.datetime.now().strftime('%Y-%m-%d')
    concept_type_dataset: str = CONCEPT_TYPE_DATASET
    dataset_version: Optional[str] = None
    dataset_keyword: List[str] = DATASET_KEYWORD
    dataset_has_frequency_publication_frequency: str = PUBLICATION_FREQUENCY
    procurement_public_issued_by_country: Optional[str]
    procurement_public_url_etendering: Optional[List[str]]


class ExpressionMetadata(Metadata):
    identifier: Optional[str]
    title: Optional[Dict[str, str]] = None
    uses_language: str = USES_LANGUAGE


class ManifestationMetadata(Metadata):
    identifier: Optional[str]
    type: str = MANIFESTATION_TYPE
    date_publication: str = datetime.datetime.now().strftime('%Y-%m-%d')
    distribution_has_status_distribution_status: str = DISTRIBUTION_STATUS
    distribution_has_media_type_concept_media_type: str = MEDIA_TYPE


class PackagerMetadata(Metadata):
    notice: NoticeMetadata = NoticeMetadata()
    mets: MetsMetadata = MetsMetadata()
    work: WorkMetadata = WorkMetadata()
    expression: ExpressionMetadata = ExpressionMetadata()
    manifestation: ManifestationMetadata = ManifestationMetadata()
