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
from abc import ABC
from datetime import datetime
from enum import IntEnum
from functools import total_ordering
from typing import Optional, List, Union

from pydantic import Field, computed_field

from ted_sws.core.model import PropertyBaseModel
from ted_sws.core.model.lazy_object import LazyObjectABC, LazyObjectFieldsLoaderABC
from ted_sws.core.model.manifestation import METSManifestation, RDFManifestation, XMLManifestation, \
    RDFValidationManifestation, SPARQLTestSuiteValidationReport, SHACLTestSuiteValidationReport, \
    XPATHCoverageValidationReport, XMLValidationManifestation, ValidationSummaryReport
from ted_sws.core.model.metadata import TEDMetadata, NormalisedMetadata, XMLMetadata


class UnsupportedStatusTransition(Exception):
    pass


@total_ordering
class NoticeStatus(IntEnum):
    """
        The status of the notice in the pipeline
    """
    RAW = 10
    INDEXED = 15
    # STATES FOR RE-TRANSFORM ---BEGIN---
    NORMALISED_METADATA = 20
    INELIGIBLE_FOR_TRANSFORMATION = 23  # backlog status
    ELIGIBLE_FOR_TRANSFORMATION = 27  # forward status
    PREPROCESSED_FOR_TRANSFORMATION = 29
    TRANSFORMED = 30
    # STATES FOR RE-VALIDATE---BEGIN---
    DISTILLED = 35
    # STATES FOR RE-TRANSFORM ---END---
    # STATES FOR RE-VALIDATE---END---
    # STATES FOR RE-PACKAGE ---BEGIN---
    VALIDATED = 40
    INELIGIBLE_FOR_PACKAGING = 43  # backlog status
    ELIGIBLE_FOR_PACKAGING = 47  # forward status
    # STATES FOR RE-PACKAGE ---END---
    # STATES FOR RE-PUBLISH ---BEGIN---
    PACKAGED = 50
    INELIGIBLE_FOR_PUBLISHING = 53  # backlog status
    ELIGIBLE_FOR_PUBLISHING = 57  # forward status
    # STATES FOR RE-PUBLISH ---END---
    PUBLISHED = 60
    PUBLICLY_UNAVAILABLE = 63  # to be investigated if more fine-grained checks can be adopted #TODO: Revalidate for public availability.
    PUBLICLY_AVAILABLE = 67  # forward status

    def __lt__(self, other):
        if type(other) == type(self):
            return self.value < other.value
        raise ValueError(f"Cannot compare {self.name} and {other.name}")

    def __gt__(self, other):
        if type(other) == type(self):
            return self.value > other.value
        raise ValueError(f"Cannot compare {self.name} and {other.name}")

    def __str__(self):
        return self._name_


#  possible downstream transitions
NOTICE_STATUS_DOWNSTREAM_TRANSITION = {NoticeStatus.RAW: [NoticeStatus.INDEXED],
                                       NoticeStatus.INDEXED: [NoticeStatus.NORMALISED_METADATA],
                                       NoticeStatus.NORMALISED_METADATA: [NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION,
                                                                          NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION],
                                       NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION: [
                                           NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION],
                                       NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION: [
                                           NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION],
                                       NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION: [NoticeStatus.TRANSFORMED],
                                       NoticeStatus.TRANSFORMED: [NoticeStatus.DISTILLED],
                                       NoticeStatus.DISTILLED: [NoticeStatus.VALIDATED],
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

    created_at: str = datetime.now().replace(microsecond=0).isoformat()
    version_number: int = 0

    @computed_field
    @property
    def status(self) -> NoticeStatus:
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


class LazyWorkExpression(WorkExpression, LazyObjectABC, ABC):
    _lazy_object_fields_loader: LazyObjectFieldsLoaderABC = None

    def set_lazy_object_fields_loader(self, lazy_object_fields_loader: LazyObjectFieldsLoaderABC):
        """

        :param lazy_object_fields_loader:
        :return:
        """
        self._lazy_object_fields_loader = lazy_object_fields_loader

    def get_lazy_object_fields_loader(self) -> Optional[LazyObjectFieldsLoaderABC]:
        """

        :return:
        """
        return self._lazy_object_fields_loader


class Notice(LazyWorkExpression):
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
    _status: NoticeStatus = NoticeStatus.RAW
    ted_id: str = Field(..., allow_mutation=False)
    _original_metadata: Optional[TEDMetadata] = None
    _xml_manifestation: Optional[XMLManifestation] = None
    _normalised_metadata: Optional[NormalisedMetadata] = None
    _preprocessed_xml_manifestation: Optional[XMLManifestation] = None
    _distilled_rdf_manifestation: Optional[RDFManifestation] = None
    _rdf_manifestation: Optional[RDFManifestation] = None
    _mets_manifestation: Optional[METSManifestation] = None
    _xml_metadata: Optional[XMLMetadata] = None
    validation_summary: Optional[ValidationSummaryReport] = None

    @computed_field
    @property
    def original_metadata(self) -> Optional[TEDMetadata]:
        if self._original_metadata is None:
            self.load_lazy_field(property_field=Notice.original_metadata)
        return self._original_metadata

    @computed_field
    @property
    def xml_manifestation(self) -> XMLManifestation:
        if self._xml_manifestation is None:
            self.load_lazy_field(property_field=Notice.xml_manifestation)
        return self._xml_manifestation

    def set_original_metadata(self, ted_metadata: TEDMetadata):
        self._original_metadata = ted_metadata

    def set_xml_manifestation(self, xml_manifestation: XMLManifestation):
        self._xml_manifestation = xml_manifestation

    @computed_field
    @property
    def xml_metadata(self) -> XMLMetadata:
        if self._xml_metadata is None:
            self.load_lazy_field(property_field=Notice.xml_metadata)
        return self._xml_metadata

    @computed_field
    @property
    def preprocessed_xml_manifestation(self) -> XMLManifestation:
        if self._preprocessed_xml_manifestation is None:
            self.load_lazy_field(property_field=Notice.preprocessed_xml_manifestation)
        return self._preprocessed_xml_manifestation

    @computed_field
    @property
    def distilled_rdf_manifestation(self) -> RDFManifestation:
        if self._distilled_rdf_manifestation is None:
            self.load_lazy_field(property_field=Notice.distilled_rdf_manifestation)
        return self._distilled_rdf_manifestation

    @computed_field
    @property
    def normalised_metadata(self) -> NormalisedMetadata:
        if self._normalised_metadata is None:
            self.load_lazy_field(property_field=Notice.normalised_metadata)
        return self._normalised_metadata

    @computed_field
    @property
    def rdf_manifestation(self) -> RDFManifestation:
        if self._rdf_manifestation is None:
            self.load_lazy_field(property_field=Notice.rdf_manifestation)
        return self._rdf_manifestation

    @computed_field
    @property
    def mets_manifestation(self) -> METSManifestation:
        if self._mets_manifestation is None:
            self.load_lazy_field(property_field=Notice.mets_manifestation)
        return self._mets_manifestation

    def get_rdf_validation(self) -> Optional[List[RDFValidationManifestation]]:
        if not self.rdf_manifestation:
            return None
        result = []
        for shacl_validation in self.rdf_manifestation.shacl_validations:
            result.append(shacl_validation)
        for sparql_validation in self.rdf_manifestation.sparql_validations:
            result.append(sparql_validation)
        return result

    def get_distilled_rdf_validation(self) -> Optional[List[RDFValidationManifestation]]:
        if not self.distilled_rdf_manifestation:
            return None
        result = []
        for shacl_validation in self.distilled_rdf_manifestation.shacl_validations:
            result.append(shacl_validation)
        for sparql_validation in self.distilled_rdf_manifestation.sparql_validations:
            result.append(sparql_validation)
        return result

    def get_xml_validation(self) -> Optional[List[XMLValidationManifestation]]:
        result = []
        if self.xml_manifestation.xpath_coverage_validation:
            result.append(self.xml_manifestation.xpath_coverage_validation)
        return result

    def set_xml_metadata(self, xml_metadata: XMLMetadata):
        """

        :param xml_metadata:
        :return:
        """
        self._xml_metadata = xml_metadata
        self.update_status_to(NoticeStatus.INDEXED)

    def set_preprocessed_xml_manifestation(self, preprocessed_xml_manifestation: XMLManifestation):
        """
            Set preprocessed XML manifestation to the notice.
        :param preprocessed_xml_manifestation:
        :return:
        """
        if self.preprocessed_xml_manifestation == preprocessed_xml_manifestation:
            return
        self._preprocessed_xml_manifestation = preprocessed_xml_manifestation
        self.update_status_to(NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION)

    def set_distilled_rdf_manifestation(self, distilled_rdf_manifestation: RDFManifestation):
        """
            Set distilled RDF manifestation to the notice.
        :param distilled_rdf_manifestation:
        :return:
        """
        if self.distilled_rdf_manifestation == distilled_rdf_manifestation:
            return
        self._distilled_rdf_manifestation = distilled_rdf_manifestation
        self.update_status_to(NoticeStatus.DISTILLED)

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
        if (not rdf_manifestation.sparql_validations) and (not rdf_manifestation.shacl_validations):
            self.update_status_to(NoticeStatus.TRANSFORMED)
        else:
            self.update_status_to(NoticeStatus.VALIDATED)

    def _check_status_is_validated(self) -> bool:
        """

        :return:
        """
        if self.rdf_manifestation and self.distilled_rdf_manifestation and self.xml_manifestation:
            if self.distilled_rdf_manifestation.is_validated() and self.xml_manifestation.is_validated():
                return True
        return False

    def set_rdf_validation(self,
                           rdf_validation: Union[SPARQLTestSuiteValidationReport, SHACLTestSuiteValidationReport]):
        """
            Add an RDF validation result to the notice.
            If METS package data are available, erase them and reset the state.
        :param rdf_validation:
        :return:
        """
        if not self.rdf_manifestation:
            raise ValueError("Cannot set the RDF validation of a non-existent RDF manifestation")

        self.rdf_manifestation.add_validation(validation=rdf_validation)

    def set_distilled_rdf_validation(self, rdf_validation: Union[SPARQLTestSuiteValidationReport,
    SHACLTestSuiteValidationReport]):
        """

        :param rdf_validation:
        :return:
        """
        if not self.distilled_rdf_manifestation:
            raise ValueError("Cannot set the RDF validation of a non-existent RDF manifestation")

        self.distilled_rdf_manifestation.add_validation(validation=rdf_validation)

        if self._check_status_is_validated():
            self.update_status_to(NoticeStatus.VALIDATED)

    def set_xml_validation(self, xml_validation: Union[XPATHCoverageValidationReport]):
        """
            Add an XML validation result to the notice.
        :param xml_validation:
        :return:
        """
        self.xml_manifestation.add_validation(validation=xml_validation)
        if self._check_status_is_validated():
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

    def mark_as_published(self):
        """
            Mark a notice as published.
        :return:
        """
        if self.status < NoticeStatus.PUBLISHED:
            self.update_status_to(NoticeStatus.PUBLISHED)

    def set_is_publicly_available(self, availability: bool):
        """

        :param availability:
        :return:
        """
        if not availability:
            self.update_status_to(NoticeStatus.PUBLICLY_UNAVAILABLE)
        else:
            self.update_status_to(NoticeStatus.PUBLICLY_AVAILABLE)

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
            raise ValueError("Status must be a NoticeStatus")

        if self._status < new_status:
            if new_status in NOTICE_STATUS_DOWNSTREAM_TRANSITION[self._status]:
                self._status = new_status
            else:
                raise UnsupportedStatusTransition(
                    f"Unsupported transition from state {self._status} to state {new_status}.")
        elif self._status > new_status:
            self._status = new_status
            if new_status < NoticeStatus.INDEXED:
                self.remove_lazy_field(Notice.xml_metadata)
                self._xml_metadata = None
            if new_status < NoticeStatus.NORMALISED_METADATA:
                self.remove_lazy_field(Notice.normalised_metadata)
                self._normalised_metadata = None
                # TODO: preprocessed_xml_manifestation is the same as xml_manifestation
                # if delete preprocessed xml manifestation will delete xml_manifestation
                # in future remove _preprocessed_xml_manifestation field from model
                self._preprocessed_xml_manifestation = None
            if new_status < NoticeStatus.TRANSFORMED:
                self.remove_lazy_field(Notice.rdf_manifestation)
                self.remove_lazy_field(Notice.distilled_rdf_manifestation)
                self._rdf_manifestation = None
                self._distilled_rdf_manifestation = None
            if new_status < NoticeStatus.PACKAGED:
                self.remove_lazy_field(Notice.mets_manifestation)
                self._mets_manifestation = None
