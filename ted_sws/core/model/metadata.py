#!/usr/bin/python3

# metadata.py
# Date:  09/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from typing import List, Optional

from pydantic.annotated_types import NamedTuple

from ted_sws.core.model import PropertyBaseModel


class Metadata(PropertyBaseModel):
    """
        Unified interface for metadata
    """

    class Config:
        underscore_attrs_are_private = True


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
    city_of_buyer: Optional[List[LanguageTaggedString]]
    name_of_buyer: Optional[List[LanguageTaggedString]]
    original_language: Optional[str]
    country_of_buyer: Optional[str]
    eu_institution: Optional[bool]
    document_sent_date: Optional[str]
    deadline_for_submission: Optional[str]
    notice_type: str
    form_type: str
    place_of_performance: Optional[List[str]]
    extracted_legal_basis_directive: Optional[str]
    legal_basis_directive: str
    form_number: str
    eforms_subtype: str
    xsd_version: str


class TEDMetadata(Metadata):
    """
        Stores notice original metadata
    """
    AA: str = None
    AC: str = None
    CY: str = None
    DD: str = None
    DI: str = None
    DS: str = None
    DT: str = None
    MA: str = None
    NC: str = None
    ND: str = None
    OC: List[str] = None
    OJ: str = None
    OL: str = None
    OY: List[str] = None
    PC: List[str] = None
    PD: str = None
    PR: str = None
    RC: List[str] = None
    RN: int = None
    RP: str = None
    TD: str = None
    TVH: str = None
    TVL: str = None
    TY: str = None
