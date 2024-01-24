#!/usr/bin/python3

# test_metadata_transformer.py
# Date:  09/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

""" """
from ted_sws.core.model.metadata import NormalisedMetadata
from ted_sws.notice_metadata_processor.model.metadata import ExtractedMetadata
from ted_sws.notice_packager.services.metadata_transformer import MetadataTransformer, publication_notice_uri, \
    publication_notice_year, publication_work_identifier, publication_notice_number, NORMALIZED_SEPARATOR


def test_notice_metadata(notice_sample_metadata: NormalisedMetadata):
    assert isinstance(notice_sample_metadata, NormalisedMetadata)


def test_metadata_transformer(notice_sample_metadata: NormalisedMetadata):
    metadata_transformer = MetadataTransformer(notice_sample_metadata)
    template_metadata = metadata_transformer.template_metadata()

    assert hasattr(template_metadata, "notice")
    assert hasattr(template_metadata, "work")
    assert hasattr(template_metadata, "expression")
    assert hasattr(template_metadata, "manifestation")


def test_publication_notice_year(notice_sample_metadata):
    year = publication_notice_year(notice_sample_metadata)
    assert year == "2018"


def test_publication_notice_number(notice_id):
    notice_number = publication_notice_number(notice_id)
    assert notice_number == "196390"

    glued_notice_id = notice_id.replace(NORMALIZED_SEPARATOR, "")
    notice_number = publication_notice_number(glued_notice_id)
    assert notice_number == "1963902018"


def test_publication_notice_uri(notice_id, notice_sample_metadata):
    uri = publication_notice_uri(notice_id, notice_sample_metadata)
    assert uri == "http://data.europa.eu/a4g/resource/2018/196390_2018"


def test_publication_work_identifier(notice_id, notice_sample_metadata):
    work_id = publication_work_identifier(notice_id, notice_sample_metadata)
    assert work_id == "2018_S_22_196390"

