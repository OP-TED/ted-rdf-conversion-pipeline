#!/usr/bin/python3

# metadata.py
# Date:  22/02/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

"""
This model contains the metadata mapping/manipulation class to be used by Notice-Packager/Template-Generator
"""
import datetime

from ted_sws.domain.model.metadata import Metadata, NormalisedMetadata
from typing import List, Dict, Any


WORK_AGENT = "PUBL"
BASE_CORPORATE_BODY = "&cellar-authority;corporate-body/"
BASE_WORK = "http://data.europa.eu/a4g/resource/"

WORK_DO_NOT_INDEX = "true"
LANGUAGES = ["en"]

ACTION_CREATE = "create"
ACTION_UPDATE = "update"
ACCEPTED_ACTIONS = [ACTION_CREATE, ACTION_UPDATE]


def validate_notice_action_type(v):
    if v not in ACCEPTED_ACTIONS:
        raise ValueError('No such action: %s' % v)


class MetaMetadata(Metadata):
    class Config:
        underscore_attrs_are_private = True


class NoticeActionMetadata(MetaMetadata):
    """
    Notice action metadata
    """
    type: Any = "create"
    date: Any = datetime.datetime.now()


class NoticeMetadata(Metadata):
    """
    General notice metadata
    """
    id: Any
    languages: List[Any] = LANGUAGES
    action: NoticeActionMetadata = NoticeActionMetadata()


class WorkMetadata(MetaMetadata):
    """
        What is the minimal input necessary to produce the work metadata,
        and the rest is a bunch of constants OR generated values (e.g. date, URI, ...)
    """

    do_not_index: Any = WORK_DO_NOT_INDEX
    date_document: Any = datetime.date.today()
    created_by_agent: Any = WORK_AGENT
    dataset_published_by_agent: Any = WORK_AGENT
    datetime_transmission: Any = None
    title: Dict[Any, Any] = None
    date_creation: Any = None
    dataset_version: Any = None
    dataset_keyword: List[Any] = None
    dataset_has_frequency_publication_frequency: Any = None

    @property
    def year(self):
        return "1999"

    @property
    def uri(self):
        # http://data.europa.eu/a4g/resource/2016/196390_2016
        return f"{BASE_WORK}/{self.year}/{super().notice.id}"


class ExpressionMetadata(Metadata):
    title: Dict[Any, Any] = None
    uses_language: Any = None


class ManifestationMetadata(Metadata):
    type: Any = None
    date_publication: Any = None
    distribution_has_status_distribution_status: Any = None
    distribution_has_media_type_concept_media_type: Any = None


class PackagerMetadata(Metadata):
    notice: NoticeMetadata
    work: WorkMetadata
    expression: ExpressionMetadata
    manifestation: ManifestationMetadata

    @classmethod
    def from_normalised_metadata(cls, normalised_metadata: NormalisedMetadata) -> Dict:
        metadata = PackagerMetadata()

        # NOTICE
        metadata.notice.id = None
        metadata.notice.languages = None
        metadata.notice.action.type = ACTION_CREATE
        metadata.notice.action.date = None

        # WORK
        metadata.work.do_not_index = WORK_DO_NOT_INDEX
        metadata.work.date_document = None
        metadata.work.created_by_agent = None
        metadata.work.dataset_published_by_agent = None
        metadata.work.datetime_transmission = None
        metadata.work.title = None
        metadata.work.date_creation = None
        metadata.work.dataset_version = None
        metadata.work.dataset_keyword = None
        metadata.work.dataset_has_frequency_publication_frequency = None

        # EXPRESSION
        metadata.expression.title = None
        metadata.expression.uses_language = None

        # MANIFESTATION
        metadata.manifestation.type = None
        metadata.manifestation.date_publication = None
        metadata.manifestation.distribution_has_status_distribution_status = None
        metadata.manifestation.distribution_has_media_type_concept_media_type = None

        return metadata.dict()
