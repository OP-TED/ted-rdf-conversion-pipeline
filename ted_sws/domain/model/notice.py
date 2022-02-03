#!/usr/bin/python3

# notice.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

"""
    In this module we define necessary artifacts of the notice aggregate.
    The main purpose is to provide top level access to a notice.

"""
from __future__ import annotations

from ted_sws.domain.model import NoticeStatus, WorkExpression
from ted_sws.domain.model.manifestation import METSManifestation, RDFManifestation, XMLManifestation
from ted_sws.domain.model.metadata import OriginalMetadata, NormalisedMetadata


class Notice(WorkExpression):
    """
        A TED notice in any of its forms across the TED-SWS pipeline. This class is conceptualised as a merger of Work
        and Expression in the FRBR class hierarchy and is connected to some of its Manifestations.
    """

    def __init__(self, ted_id: str, source_url: str, original_metadata: OriginalMetadata,
                 xml_manifestation: XMLManifestation):
        self._ted_id = ted_id
        self._source_url = source_url
        self._original_metadata = original_metadata
        self._embodied_xml_manifestation = xml_manifestation

        self._status = NoticeStatus.RAW

        self._normalised_metadata: NormalisedMetadata = None
        self._transformed_content: RDFManifestation = None
        self._packaged_content: METSManifestation = None

    @property
    def ted_id(self) -> str:
        return self._ted_id

    @property
    def source_url(self) -> str:
        return self._source_url

    @property
    def original_metadata(self) -> OriginalMetadata:
        return self._original_metadata

    @property
    def xml_manifestation(self) -> XMLManifestation:
        return self._embodied_xml_manifestation

    @property
    def normalised_metadata(self) -> NormalisedMetadata:
        return self._normalised_metadata

    @normalised_metadata.setter
    def normalised_metadata(self, normalised_metadata: NormalisedMetadata):
        # TODO: add logic
        self._normalised_metadata = normalised_metadata

    @property
    def transformed_content(self) -> RDFManifestation:
        return self._transformed_content

    @transformed_content.setter
    def transformed_content(self, transformed_content: bytes):
        # TODO: add logic
        self._transformed_content = transformed_content

    @property
    def packaged_content(self) -> METSManifestation:
        return self._packaged_content

    @packaged_content.setter
    def packaged_content(self, packaged_content: METSManifestation):
        # TODO: add logic
        self._packaged_content = packaged_content


