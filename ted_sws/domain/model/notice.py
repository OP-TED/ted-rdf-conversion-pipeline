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

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from ted_sws.domain.model.manifestation import METSManifestation, RDFManifestation, XMLManifestation


class NoticeStatus(Enum):
    """
        The status of the notice in the pipeline
    """
    RAW = 10
    NORMALISED_METADATA = 20
    INELIGIBLE_FOR_TRANSFORMATION = 23  # backlog status
    ELIGIBLE_FOR_TRANSFORMATION = 27  # forward status
    TRANSFORMED = 30
    VALIDATED_TRANSFORMATION = 40
    INELIGIBLE_FOR_PACKAGING = 43  # backlog status
    ELIGIBLE_FOR_PACKAGING = 47  # forward status
    PACKAGED = 50
    FAULTY_PACKAGE = 53  # backlog status
    CORRECT_PACKAGE = 57  # forward status
    PUBLISHED = 60
    PUBLICLY_UNAVAILABLE = 63  # to be investigated if more fine-grained checks can be adopted
    PUBLICLY_AVAILABLE = 67  # forward status


class WorkExpression(BaseModel):
    """
        A Merger of Work and Expression FRBR classes.

        :param created_at
            creation timestamp
        :param version_number
            Compares the current version of the object with a known version.
            This is a simple solution in the case of parallel processes which
            are updating the same object in concomitant transactions.

            Version increase can be done only by the transaction maager.
            See: https://www.cosmicpython.com/book/chapter_11_external_events.html
    """

    created_at: datetime = datetime.now()
    version_number: int = 0


class Notice(WorkExpression):
    """
        A TED notice in any of its forms across the TED-SWS pipeline. This class is conceptualised as a merger of Work
        and Expression in the FRBR class hierarchy and is connected to some of its Manifestations.
    """
    class Config:
        validate_assignment = True
        orm_mode = True

    ted_id: str = Field(..., allow_mutation=False)
    status: NoticeStatus = NoticeStatus.RAW
    source_url: Optional[str]

    original_metadata: Optional[dict]
    normalised_metadata: Optional[dict]

    xml_manifestation: XMLManifestation = Field(..., allow_mutation=False)
    rdf_manifestation: Optional[RDFManifestation] = None
    mets_manifestation: Optional[METSManifestation] = None


    # def __init__(self, ted_id: str = None, original_metadata: dict = None,
    #              xml_manifestation: XMLManifestation = None, source_url: str = None, **kwargs):
    #     super().__init__(**kwargs)
    #     self._ted_id = ted_id
    #     self._source_url = source_url
    #     self._xml_manifestation = xml_manifestation
    #     self._original_metadata = original_metadata
    #
    # @property
    # def status(self) -> NoticeStatus:
    #     return NoticeStatus[self._status]
    #
    # @property
    # def ted_id(self) -> str:
    #     return self._ted_id
    #
    # @property
    # def source_url(self) -> str:
    #     return self._source_url
    #
    # @property
    # def original_metadata(self) -> dict:
    #     """
    #     Metadata (standard forms) extracted from TED.
    #
    #     When a notice is extracted from TED it is associated with metadata as currently organised by the TED website
    #     in accordance to StandardForms. This shall be harmonised with future eForms, Cellar CDM model and possibly
    #     the Legal Analysis Methodology (LAM).
    #     :return:
    #     """
    #     return self._original_metadata
    #
    # @property
    # def normalised_metadata(self) -> dict:
    #     """
    #     Metadata harmonised by taking into consideration standard forms, eForms, Cellar CDM model
    #     and possibly the Legal Analysis Methodology (LAM).
    #     :return:
    #     """
    #     return self._normalised_metadata
    #
    # @normalised_metadata.setter
    # def normalised_metadata(self, normalised_metadata: dict):
    #     """
    #         Set notice normalised metadata.
    #         If any future state data are available, erase them and reset the state.
    #     :param normalised_metadata:
    #     :return:
    #     """
    #     if self._normalised_metadata:
    #         self._rdf_manifestation = None
    #         self._mets_manifestation = None
    #
    #     self._normalised_metadata = normalised_metadata
    #     self._status = NoticeStatus.NORMALISED_METADATA.name
    #
    # # @property
    # # def xml_manifestation(self) -> XMLManifestation:
    # #     return self._xml_manifestation
    #
    # @property
    # def transformed_content(self) -> RDFManifestation:
    #     return self._transformed_content
    #
    # @transformed_content.setter
    # def transformed_content(self, transformed_content: bytes):
    #     # TODO: add logic
    #     self._transformed_content = transformed_content
    #
    # @property
    # def mets_manifestation(self) -> METSManifestation:
    #     return self._mets_manifestation
    #
    # @mets_manifestation.setter
    # def packaged_content(self, packaged_content: METSManifestation):
    #     # TODO: add logic
    #     self._packaged_content = packaged_content

    def __str__(self):
        return f"/Notice ({self.status.name}): {self.ted_id}/"
