#!/usr/bin/python3

# metadata_transformer.py
# Date:  22/02/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

"""
This module provides transformers for notice metadata (original or normalized)
into data structures needed to render the templates.
This transformed metadata is what adapters expect.
"""

import datetime

from ted_sws.notice_metadata_processor.model.metadata import ExtractedMetadata
from ted_sws.notice_packager.model.metadata import PackagerMetadata, ACTION_CREATE, LANGUAGE, REVISION, BASE_WORK, \
    BASE_TITLE

# This is used in pipeline
NORMALIZED_SEPARATOR = '_'

# This is used in TED API
DENORMALIZED_SEPARATOR = '-'

PROCUREMENT_PUBLIC = "procurement_public"
PROCUREMENT_NOTICE = "PROCUREMENT_NOTICE"


class MetadataTransformer:
    def __init__(self, notice_metadata: ExtractedMetadata):
        self.notice_metadata = notice_metadata

    def template_metadata(self, action: str = ACTION_CREATE) -> PackagerMetadata:
        metadata = self.from_notice_metadata(self.notice_metadata)
        metadata.notice.action.type = action
        return metadata

    @classmethod
    def normalize_value(cls, value: str) -> str:
        """
        The initial (TED API) separator is replaced with pipeline's one.
        This is used when notice comes in from API
        :param value:
        :return:
        """
        return value.replace(DENORMALIZED_SEPARATOR, NORMALIZED_SEPARATOR)

    @classmethod
    def denormalize_value(cls, value: str) -> str:
        """
        The pipeline's separator is replaced with initial (TED API)'s one.
        This is used when notice goes out to API
        :param value:
        :return:
        """
        return value.replace(NORMALIZED_SEPARATOR, DENORMALIZED_SEPARATOR)

    @classmethod
    def from_notice_metadata(cls, notice_metadata: ExtractedMetadata) -> PackagerMetadata:
        _date = datetime.datetime.now()
        _revision = REVISION

        metadata = PackagerMetadata()

        # NOTICE
        metadata.notice.id = cls.normalize_value(notice_metadata.notice_publication_number)

        # WORK
        metadata.work.identifier = publication_work_identifier(metadata.notice.id, notice_metadata)
        metadata.work.cdm_rdf_type = PROCUREMENT_PUBLIC
        metadata.work.resource_type = PROCUREMENT_NOTICE
        metadata.work.date_document = notice_metadata.publication_date
        metadata.work.uri = publication_notice_uri(metadata.notice.id)
        title_search = [t.title.text for t in notice_metadata.title if t.title.language == LANGUAGE.upper()]
        if len(title_search) > 0:
            metadata.work.title = {LANGUAGE: title_search[0]}
        metadata.work.date_creation = datetime.datetime \
            .strptime(notice_metadata.publication_date, '%Y%m%d').strftime('%Y-%m-%d')
        metadata.work.dataset_version = _date.strftime('%Y%m%d') + '-' + _revision
        metadata.work.procurement_public_issued_by_country = notice_metadata.country_of_buyer
        metadata.work.procurement_public_url_etendering = notice_metadata.uri_list

        # EXPRESSION
        metadata.expression.title = {LANGUAGE: BASE_TITLE + " " + metadata.notice.id}

        # MANIFESTATION
        metadata.manifestation.date_publication = notice_metadata.publication_date
        return metadata


def publication_notice_year(notice_id):
    return notice_id.split(NORMALIZED_SEPARATOR)[1]


def publication_notice_number(notice_id):
    return notice_id.split(NORMALIZED_SEPARATOR)[0]


def publication_notice_uri(notice_id):
    return f"{BASE_WORK}{publication_notice_year(notice_id)}/{notice_id}"


def publication_work_identifier(notice_id, notice_metadata):
    year = publication_notice_year(notice_id)
    number = publication_notice_number(notice_id)
    return f"{year}_{notice_metadata.ojs_type}_{notice_metadata.ojs_issue_number}_{number}"
