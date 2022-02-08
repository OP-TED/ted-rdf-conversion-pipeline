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

from schematics.types import DictType, StringType, ModelType

from ted_sws.domain.model import NoticeStatus, WorkExpression
from ted_sws.domain.model.manifestation import METSManifestation, RDFManifestation, XMLManifestation


class Notice(WorkExpression):
    """
        A TED notice in any of its forms across the TED-SWS pipeline. This class is conceptualised as a merger of Work
        and Expression in the FRBR class hierarchy and is connected to some of its Manifestations.
    """

    class Options:
        serialize_when_none = False

    _status = StringType(serialized_name="status", required=True, choices=[status.name for status in NoticeStatus],
                         default=NoticeStatus.RAW.name, )
    _ted_id = StringType(serialized_name="ted_id", required=True)
    _source_url = StringType(serialized_name="source_url")

    _original_metadata = DictType(field=StringType, serialized_name="original_metadata")
    _normalised_metadata = DictType(field=StringType, serialized_name="normalised_metadata")

    _xml_manifestation = ModelType(XMLManifestation, serialized_name="xml_manifestation")
    _rdf_manifestation = ModelType(RDFManifestation, serialized_name="rdf_manifestation")
    _mets_manifestation = ModelType(METSManifestation, serialized_name="mets_manifestation")

    @classmethod
    def new(cls, ted_id, source_url, xml_manifestation, original_metadata=None):
        result = cls()
        result._ted_id = ted_id
        result._source_url = source_url
        result._xml_manifestation = xml_manifestation
        result._original_metadata = original_metadata if original_metadata else None

        return result

    @property
    def status(self) -> NoticeStatus:
        return NoticeStatus[self._status]

    @property
    def ted_id(self) -> str:
        return self._ted_id

    @property
    def source_url(self) -> str:
        return self._source_url

    @property
    def original_metadata(self) -> dict:
        """
        Metadata (standard forms) extracted from TED.

        When a notice is extracted from TED it is associated with metadata as currently organised by the TED website
        in accordance to StandardForms. This shall be harmonised with future eForms, Cellar CDM model and possibly
        the Legal Analysis Methodology (LAM).
        :return:
        """
        return self._original_metadata

    @property
    def normalised_metadata(self) -> dict:
        """
        Metadata harmonised by taking into consideration standard forms, eForms, Cellar CDM model
        and possibly the Legal Analysis Methodology (LAM).
        :return:
        """
        return self._normalised_metadata

    @normalised_metadata.setter
    def normalised_metadata(self, normalised_metadata: dict):
        # TODO: add logic
        self._normalised_metadata = normalised_metadata

    @property
    def xml_manifestation(self) -> XMLManifestation:
        return self._xml_manifestation

    @property
    def transformed_content(self) -> RDFManifestation:
        return self._transformed_content

    @transformed_content.setter
    def transformed_content(self, transformed_content: bytes):
        # TODO: add logic
        self._transformed_content = transformed_content

    @property
    def mets_manifestation(self) -> METSManifestation:
        return self._mets_manifestation

    @mets_manifestation.setter
    def packaged_content(self, packaged_content: METSManifestation):
        # TODO: add logic
        self._packaged_content = packaged_content
