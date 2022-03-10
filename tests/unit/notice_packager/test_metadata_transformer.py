#!/usr/bin/python3

# test_metadata_transformer.py
# Date:  09/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

""" """

from ted_sws.notice_packager.services.metadata_transformer import MetadataTransformer
from ted_sws.metadata_normaliser.model.metadata import ExtractedMetadata


def test_notice_metadata(notice_sample_metadata: ExtractedMetadata):
    assert isinstance(notice_sample_metadata, ExtractedMetadata)


def test_metadata_transformer(notice_sample_metadata: ExtractedMetadata):
    metadata_transformer = MetadataTransformer(notice_sample_metadata)
    template_metadata = metadata_transformer.template_metadata()

    assert "notice" in template_metadata
    assert "work" in template_metadata
    assert "expression" in template_metadata
    assert "manifestation" in template_metadata

