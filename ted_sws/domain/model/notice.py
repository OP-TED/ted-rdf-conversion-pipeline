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

import abc
from datetime import datetime
from enum import Enum
from typing import Optional
from functools import total_ordering

from pydantic import Field

from ted_sws.domain.model import PropertyBaseModel
from ted_sws.domain.model.manifestation import METSManifestation, RDFManifestation, XMLManifestation, \
    RDFValidationManifestation
from ted_sws.domain.model.metadata import TEDMetadata, NormalisedMetadata


class UnsupportedStatusTransition(Exception):
    pass


@total_ordering
class NoticeStatus(Enum):
    """
        The status of the notice in the pipeline
    """
    RAW = 10
    NORMALISED_METADATA = 20
    INELIGIBLE_FOR_TRANSFORMATION = 23  # backlog status
    ELIGIBLE_FOR_TRANSFORMATION = 27  # forward status
    TRANSFORMED = 30
    VALIDATED = 40
    INELIGIBLE_FOR_PACKAGING = 43  # backlog status
    ELIGIBLE_FOR_PACKAGING = 47  # forward status
    PACKAGED = 50
    INELIGIBLE_FOR_PUBLISHING = 53  # backlog status
    ELIGIBLE_FOR_PUBLISHING = 57  # forward status
    PUBLISHED = 60
    PUBLICLY_UNAVAILABLE = 63  # to be investigated if more fine-grained checks can be adopted
    PUBLICLY_AVAILABLE = 67  # forward status

    def __lt__(self, other):
        if type(other) == type(self):
            return self.value < other.value
        raise ValueError(f"Cannot compare {self.name} and {other.name}")

    def __gt__(self, other):
        if type(other) == type(self):
            return self.value > other.value
        raise ValueError(f"Cannot compare {self.name} and {other.name}")


#  possible downstream transitions
NOTICE_STATUS_DOWNSTREAM_TRANSITION = {NoticeStatus.RAW: [NoticeStatus.NORMALISED_METADATA],
                                       NoticeStatus.NORMALISED_METADATA: [NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION,
                                                                          NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION],
                                       NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION: [
                                           NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION],
                                       NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION: [NoticeStatus.TRANSFORMED],
                                       NoticeStatus.TRANSFORMED: [NoticeStatus.VALIDATED],
                                       NoticeStatus.VALIDATED: [NoticeStatus.INELIGIBLE_FOR_PACKAGING,
                                                                NoticeStatus.ELIGIBLE_FOR_PACKAGING],
                                       NoticeStatus.INELIGIBLE_FOR_PACKAGING: [NoticeStatus.ELIGIBLE_FOR_PACKAGING],
                                       NoticeStatus.ELIGIBLE_FOR_PACKAGING: [NoticeStatus.PACKAGED],
                                       NoticeStatus.PACKAGED: [NoticeStatus.INELIGIBLE_FOR_PUBLISHING,
                                                               NoticeStatus.ELIGIBLE_FOR_PUBLISHING],
                                       NoticeStatus.INELIGIBLE_FOR_PUBLISHING: [NoticeStatus.ELIGIBLE_FOR_PUBLISHING],
                                       NoticeStatus.ELIGIBLE_FOR_PUBLISHING: [NoticeStatus.PUBLISHED],
                                       NoticeStatus.PUBLISHED: [NoticeStatus.PUBLICLY_AVAILABLE,
                                                                NoticeStatus.PUBLICLY_UNAVAILABLE],
                                       NoticeStatus.PUBLICLY_UNAVAILABLE: [NoticeStatus.PUBLICLY_AVAILABLE],
                                       NoticeStatus.PUBLICLY_AVAILABLE: [],
                                       }


class WorkExpression(PropertyBaseModel, abc.ABC):
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

    @property
    def status(self):
        return self._status

    @abc.abstractmethod
    def update_status_to(self, new_status):
        """
            This solution of non-standard setters on controlled fields is adopted until
            the https://github.com/samuelcolvin/pydantic/issues/935 is solved.

            Meanwhile we can adopt a transition logic (which is not the same as validation logic).
        :param new_status:
        :return:
        """


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

        :parameter xml_manifestation
        The original XML manifestation of the notice as downloaded from the TED website.

    """
    _status: NoticeStatus = NoticeStatus.RAW  # PrivateAttr(default=NoticeStatus.RAW)
    ted_id: str = Field(..., allow_mutation=False)
    original_metadata: Optional[TEDMetadata] = None
    _normalised_metadata: Optional[NormalisedMetadata] = None

    xml_manifestation: XMLManifestation = Field(..., allow_mutation=False)
    _rdf_manifestation: Optional[RDFManifestation] = None
    _mets_manifestation: Optional[METSManifestation] = None

    @property
    def normalised_metadata(self) -> NormalisedMetadata:
        return self._normalised_metadata

    @property
    def rdf_manifestation(self) -> RDFManifestation:
        return self._rdf_manifestation

    @property
    def mets_manifestation(self) -> METSManifestation:
        return self._mets_manifestation

    @property
    def rdf_validation(self) -> RDFValidationManifestation:
        if not self.rdf_manifestation:
            return None

        return self.rdf_manifestation.validation

    def set_normalised_metadata(self, normalised_metadata: NormalisedMetadata):
        """
            Add normalised metadata to the notice.
            If any future state data are available, erase them and reset the state.
        :param normalised_metadata:
        :return:
        """
        if self.normalised_metadata == normalised_metadata:
            return

        self._normalised_metadata = normalised_metadata
        self.update_status_to(NoticeStatus.NORMALISED_METADATA)

    def set_rdf_manifestation(self, rdf_manifestation: RDFManifestation):
        """
            Add an RDF manifestation to the notice. The RDF manifestation can have a validation but usually not yet.
            If METS package data are available, erase them and reset the state.
        :param rdf_manifestation:
        :return:
        """
        if self.rdf_manifestation == rdf_manifestation:
            return
        self._rdf_manifestation = rdf_manifestation
        if not rdf_manifestation.validation:
            self.update_status_to(NoticeStatus.TRANSFORMED)
        else:
            self.update_status_to(NoticeStatus.VALIDATED)

    def set_rdf_validation(self, rdf_validation: RDFValidationManifestation):
        """
            Add an RDF validation result to the notice.
            If METS package data are available, erase them and reset the state.
        :param rdf_validation:
        :return:
        """
        if not self.rdf_manifestation:
            raise ValueError("Cannot set the RDF validation of a non-existent RDF manifestation")

        if self.rdf_manifestation.validation == rdf_validation:
            return

        self._rdf_manifestation.validation = rdf_validation
        self.update_status_to(NoticeStatus.VALIDATED)

    def set_mets_manifestation(self, mets_manifestation: METSManifestation):
        """
            Add a METS package manifestation to the notice.
        :param mets_manifestation:
        :return:
        """
        if not self.rdf_manifestation:
            raise ValueError("Cannot set the METS package of a non-existent RDF manifestation")

        if self.mets_manifestation is mets_manifestation:
            return

        self._mets_manifestation = mets_manifestation
        self.update_status_to(NoticeStatus.PACKAGED)

    def set_is_eligible_for_transformation(self, eligibility: bool):
        """
            Marks the notice as being eligible or not for the transformation.
            Perform the marking only if it is not already eligible.

        :param eligibility:
        :return:
        """
        if not eligibility:
            self.update_status_to(NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION)
        else:
            if self.status < NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION:
                self.update_status_to(NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION)

    def set_is_eligible_for_packaging(self, eligibility: bool):
        """
            Marks the notice as being eligible or not for the packaging.
            Perform the marking only if it is not already eligible.

        :param eligibility:
        :return:
        """
        if not eligibility:
            self.update_status_to(NoticeStatus.INELIGIBLE_FOR_PACKAGING)
        else:
            if self.status < NoticeStatus.ELIGIBLE_FOR_PACKAGING:
                self.update_status_to(NoticeStatus.ELIGIBLE_FOR_PACKAGING)

    def set_is_eligible_for_publishing(self, eligibility: bool):
        """
            Marks the notice as being eligible or not for the publishing.
            Perform the marking only if it is not already eligible.

        :param eligibility:
        :return:
        """
        if not eligibility:
            self.update_status_to(NoticeStatus.INELIGIBLE_FOR_PUBLISHING)
        else:
            if self.status < NoticeStatus.ELIGIBLE_FOR_PUBLISHING:
                self.update_status_to(NoticeStatus.ELIGIBLE_FOR_PUBLISHING)

    def __str__(self) -> str:
        return f"/Notice ({self.status.name}): {self.ted_id}/"

    def update_status_to(self, new_status: NoticeStatus):
        """
        Will update the status downstream only if the transition is unsupported. All upstream transitions are
        supported, which leads to erasing any data associated with a downstream status. For example if current state
        is "published", and teh state is regressed to "validated" then the METS data are lost.

        :param new_status:
        :return:
        """
        if type(new_status) is not NoticeStatus:
            raise ValueError(f"Status must be a NoticeStatus")

        if self._status < new_status:
            if new_status in NOTICE_STATUS_DOWNSTREAM_TRANSITION[self._status]:
                self._status = new_status
            else:
                raise UnsupportedStatusTransition(
                    f"Unsupported transition from state {self._status} to state {new_status}.")
        elif self._status > new_status:
            self._status = new_status
            if new_status < NoticeStatus.NORMALISED_METADATA:
                self._normalised_metadata = None
            if new_status < NoticeStatus.TRANSFORMED:
                self._rdf_manifestation = None
            if new_status < NoticeStatus.PACKAGED:
                self._mets_manifestation = None
