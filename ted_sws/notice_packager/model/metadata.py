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

WORK_AGENT = "PUBL"
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

ACTION_CREATE = "create"
ACTION_UPDATE = "update"
ACCEPTED_ACTIONS = [ACTION_CREATE, ACTION_UPDATE]

REVISION = "0"


def validate_notice_action_type(v):
    if v not in ACCEPTED_ACTIONS:
        raise ValueError('No such action: %s' % v)


class NoticeActionMetadata(Metadata):
    """
    Notice action metadata
    """
    type: str = ACTION_CREATE
    date: str = datetime.datetime.now().isoformat()

    @validator('type')
    def validate_notice_action_type(cls, v):
        validate_notice_action_type(v)
        return v


class NoticeMetadata(Metadata):
    """
    General notice metadata
    """
    id: Optional[str] = None
    languages: List[str] = LANGUAGES
    action: NoticeActionMetadata = NoticeActionMetadata()


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
    title: Optional[Dict[str, str]] = None
    uses_language: str = USES_LANGUAGE


class ManifestationMetadata(Metadata):
    type: str = MANIFESTATION_TYPE
    date_publication: str = datetime.datetime.now().strftime('%Y-%m-%d')
    distribution_has_status_distribution_status: str = DISTRIBUTION_STATUS
    distribution_has_media_type_concept_media_type: str = MEDIA_TYPE


class PackagerMetadata(Metadata):
    notice: NoticeMetadata = NoticeMetadata()
    work: WorkMetadata = WorkMetadata()
    expression: ExpressionMetadata = ExpressionMetadata()
    manifestation: ManifestationMetadata = ManifestationMetadata()
