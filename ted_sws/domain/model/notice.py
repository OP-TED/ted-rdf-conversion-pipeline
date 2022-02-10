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

from pydantic import Field

from ted_sws.domain.model import PropertyBaseModel
from ted_sws.domain.model.manifestation import METSManifestation, RDFManifestation, XMLManifestation
from ted_sws.domain.model.metadata import TEDMetadata, NormalizedMetadata


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


NOTICE_STATE_MAP = {NoticeStatus.RAW: [NoticeStatus.NORMALISED_METADATA],
                    NoticeStatus.NORMALISED_METADATA: [NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION,
                                                       NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION],
                    NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION: [NoticeStatus.TRANSFORMED],
                    NoticeStatus.TRANSFORMED: [NoticeStatus.VALIDATED_TRANSFORMATION],
                    NoticeStatus.VALIDATED_TRANSFORMATION: [NoticeStatus.INELIGIBLE_FOR_PACKAGING,
                                                            NoticeStatus.ELIGIBLE_FOR_PACKAGING],
                    NoticeStatus.ELIGIBLE_FOR_PACKAGING: [NoticeStatus.PACKAGED],
                    NoticeStatus.PACKAGED: [NoticeStatus.FAULTY_PACKAGE, NoticeStatus.CORRECT_PACKAGE],
                    NoticeStatus.CORRECT_PACKAGE: [NoticeStatus.PUBLISHED],
                    NoticeStatus.PUBLISHED: [NoticeStatus.PUBLICLY_AVAILABLE, NoticeStatus.PUBLICLY_UNAVAILABLE]}


class WorkExpression(PropertyBaseModel):
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

    class Config:
        underscore_attrs_are_private = True
        validate_assignment = True
        orm_mode = True

    created_at: datetime = datetime.now()
    version_number: int = 0
    _status: NoticeStatus = NoticeStatus.RAW  # PrivateAttr(default=NoticeStatus.RAW)

    @property
    def status(self):
        return self._status

    def update_status_to(self, value):
        """
            This solution of non-standard setters on controlled fields is adopted until
            the https://github.com/samuelcolvin/pydantic/issues/935 is solved.

            Meanwhile we can adopt a transition logic (which is not the same as validation logic).
        :param value:
        :return:
        """

        if value in NOTICE_STATE_MAP[self._status]:
            self._status = value
        else:
            raise Exception(f"Invalid transition from state {self._status} to state {value}")


class Notice(WorkExpression):
    """
        A TED notice in any of its forms across the TED-SWS pipeline. This class is conceptualised as a merger of Work
        and Expression in the FRBR class hierarchy and is connected to some of its Manifestations.

        :parameter original_metadata
        Metadata (standard forms) extracted from TED.
        When a notice is extracted from TED it is associated with metadata as currently organised by the TED website
        in accordance to StandardForms. This shall be harmonised with future eForms, Cellar CDM model and possibly
        the Legal Analysis Methodology (LAM).

        :parameter normalised_metadata
        Metadata harmonised by taking into consideration standard forms, eForms, Cellar CDM model
        and possibly the Legal Analysis Methodology (LAM).

    """

    ted_id: str = Field(..., allow_mutation=False)

    original_metadata: Optional[TEDMetadata] = None
    _normalised_metadata: Optional[NormalizedMetadata] = None

    xml_manifestation: XMLManifestation = Field(..., allow_mutation=False)
    _rdf_manifestation: Optional[RDFManifestation] = None
    _mets_manifestation: Optional[METSManifestation] = None

    @property
    def normalised_metadata(self):
        return self._normalised_metadata

    @property
    def rdf_manifestation(self):
        return self._rdf_manifestation

    @property
    def mets_manifestation(self):
        return self._mets_manifestation

    def set_normalised_metadata(self, normalised_metadata: NormalizedMetadata):
        """
            Set notice normalised metadata.
            If any future state data are available, erase them and reset the state.
        :param normalised_metadata:
        :return:
        """
        if self.normalised_metadata:
            self._rdf_manifestation = None
            self._mets_manifestation = None

        self._normalised_metadata = normalised_metadata
        self._status = NoticeStatus.NORMALISED_METADATA

    def set_rdf_manifestation(self, rdf_manifestation: RDFManifestation):
        """

        :param rdf_manifestation:
        :return:
        """
        self._rdf_manifestation = rdf_manifestation

    def set_mets_manifestation(self, mets_manifestation: METSManifestation):
        """

        :param mets_manifestation:
        :return:
        """
        self._mets_manifestation = mets_manifestation

    def __str__(self):
        return f"/Notice ({self.status.name}): {self.ted_id}/"
