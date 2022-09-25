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

NORM_SEP = '_'
DENORM_SEP = '-'


class MetadataTransformer:
    def __init__(self, notice_metadata: ExtractedMetadata):
        self.notice_metadata = notice_metadata

    def template_metadata(self, action: str = ACTION_CREATE) -> PackagerMetadata:
        metadata = self.from_notice_metadata(self.notice_metadata)
        metadata.notice.action.type = action
        return metadata

    @classmethod
    def normalize_value(cls, value: str) -> str:
        return value.replace(DENORM_SEP, NORM_SEP)

    @classmethod
    def denormalize_value(cls, value: str) -> str:
        return value.replace(NORM_SEP, DENORM_SEP)

    @classmethod
    def from_notice_metadata(cls, notice_metadata: ExtractedMetadata) -> PackagerMetadata:
        _date = datetime.datetime.now()
        _revision = REVISION

        metadata = PackagerMetadata()

        # NOTICE
        metadata.notice.id = cls.normalize_value(notice_metadata.notice_publication_number)

        # WORK
        metadata.work.uri = publication_notice_uri(metadata.notice.id)
        title_search = [t.title.text for t in notice_metadata.title if t.title.language == LANGUAGE.upper()]
        if len(title_search) > 0:
            metadata.work.title = {LANGUAGE: title_search[0]}
        metadata.work.date_creation = datetime.datetime \
            .strptime(notice_metadata.publication_date, '%Y%m%d').strftime('%Y-%m-%d')
        metadata.work.dataset_version = _date.strftime('%Y%m%d') + '-' + _revision

        # EXPRESSION
        metadata.expression.title = {LANGUAGE: BASE_TITLE + " " + metadata.notice.id}

        return metadata


def publication_notice_year(notice_id):
    return notice_id.split(NORM_SEP)[1]


def publication_notice_uri(notice_id):
    return f"{BASE_WORK}{publication_notice_year(notice_id)}/{notice_id}"
