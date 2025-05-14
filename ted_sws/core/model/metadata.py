#!/usr/bin/python3

# metadata.py
# Date:  09/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from enum import Enum
from typing import List, Optional, Union, NamedTuple

from pydantic import Field, validator, field_validator

from ted_sws.core.model import PropertyBaseModel


class Metadata(PropertyBaseModel):
    """
        Unified interface for metadata
    """



class XMLMetadata(Metadata):
    """
        Stores the metadata of an XMLManifestation.
    """
    unique_xpaths: List[str] = None


class LanguageTaggedString(NamedTuple):
    """
    Holds strings with language tag
    """
    text: str = None
    language: str = None


class CompositeTitle(Metadata):
    """
    Compose title
    """
    title: LanguageTaggedString = None
    title_city: LanguageTaggedString = None
    title_country: LanguageTaggedString = None


class EncodedValue(NamedTuple):
    """
    Holds code and value
    """
    code: str = None
    value: str = None


class NoticeSource(str, Enum):
    """
    Holds source of notice
    """
    STANDARD_FORM = "standard_forms"
    ELECTRONIC_FORM = "eforms"

    def __str__(self):
        return self.value


class NormalisedMetadata(Metadata):
    """
        Stores notice normalised metadata
    """
    title: List[LanguageTaggedString]
    long_title: List[LanguageTaggedString]
    notice_publication_number: str
    publication_date: str
    ojs_issue_number: str
    ojs_type: str
    city_of_buyer: Optional[List[LanguageTaggedString]] = None
    name_of_buyer: Optional[List[LanguageTaggedString]] = None
    original_language: Optional[str] = None
    country_of_buyer: Optional[str] = None
    eu_institution: Optional[bool] = None
    document_sent_date: Optional[str] = None
    deadline_for_submission: Optional[str] = None
    notice_type: str
    form_type: str
    place_of_performance: Optional[List[str]] = None
    extracted_legal_basis_directive: Optional[str] = None
    legal_basis_directive: str
    form_number: str
    eforms_subtype: str
    xsd_version: Optional[str] = None
    published_in_cellar_counter: int = Field(default=0)
    notice_source: Optional[NoticeSource] = NoticeSource.STANDARD_FORM
    eform_sdk_version: Optional[str] = None


class NormalisedMetadataView(Metadata):
    title: str
    long_title: str
    notice_publication_number: str
    publication_date: str
    ojs_issue_number: str
    ojs_type: str
    city_of_buyer: Optional[str] = None
    name_of_buyer: Optional[str] = None
    original_language: Optional[str] = None
    country_of_buyer: Optional[str] = None
    eu_institution: Optional[bool] = None
    document_sent_date: Optional[str] = None
    deadline_for_submission: Optional[str] = None
    notice_type: str
    form_type: str
    place_of_performance: Optional[List[str]] = None
    extracted_legal_basis_directive: Optional[str] = None
    legal_basis_directive: str
    form_number: str
    eforms_subtype: str
    xsd_version: Optional[str] = None
    published_in_cellar_counter: int = Field(default=0)
    notice_source: Optional[NoticeSource] = NoticeSource.STANDARD_FORM
    eform_sdk_version: Optional[str] = None


class TEDMetadata(Metadata):
    """
        Stores notice original metadata
    """
    ND: Optional[str] = None
    PD: Optional[str] = None
    # ------------------------------------------------------------------
    # Note: In TED-API v3 this field is str, in past was list
    # ------------------------------------------------------------------
    RN: Optional[Union[List[str], str]] = None
    # ------------------------------------------------------------------
    @field_validator("RN", mode="before")
    def coerce_rn(cls, value):
        if isinstance(value, list):
            return [str(item) for item in value]
        return value