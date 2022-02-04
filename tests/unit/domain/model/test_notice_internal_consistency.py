#!/usr/bin/python3

# test_notice_internal_consistency.py
# Date:  03/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from ted_sws.domain.model import NoticeMetadata
from ted_sws.domain.model.metadata import OriginalMetadata
from ted_sws.domain.model.notice import Notice
from ted_sws.domain.model.manifestation import XMLManifestation


def test_notice_creation(fetched_notice_data):
    # no notice can be created without XML manifestation, original metadata or status
    # ted_id, source_url, original_metadata, xml_manifestation = fetched_notice_data

    x = NoticeMetadata.from_dict({"key1": "value1"})

    # notice = Notice(ted_id=ted_id, source_url=source_url, original_metadata=original_metadata,
    #                 xml_manifestation=xml_manifestation)
    #
    # assert notice.original_metadata == original_metadata
    # assert notice.ted_id == ted_id
    # assert notice.xml_manifestation == xml_manifestation
    # assert notice.source_url == original_metadata
