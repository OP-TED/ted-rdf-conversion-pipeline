#!/usr/bin/python3

# metadata.py
# Date:  09/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import datetime
from typing import List, Optional

from pydantic.annotated_types import NamedTuple

from ted_sws.domain.model import PropertyBaseModel

TLanguageConceptURI = str
TCountryConceptURI = str
TEFormsNoticeTypeURI = str
TEFormsFormTypeURI = str
TNUTSConceptURI = str
TLegalBasisConceptURI = str


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
    title: List[LanguageTaggedString] = None
    long_title: List[LanguageTaggedString] = None
    notice_publication_number: str = ""
    publication_date: datetime.date = None
    ojs_issue_number: str = ""
    ojs_type: str = ""
    city_of_buyer: Optional[List[LanguageTaggedString]]
    name_of_buyer: Optional[List[LanguageTaggedString]]
    original_language: Optional[TLanguageConceptURI]
    country_of_buyer: Optional[TCountryConceptURI]
    eu_institution: Optional[bool]
    document_sent_date: Optional[datetime.date]
    deadline_for_submission: Optional[datetime.date]
    notice_type: TEFormsNoticeTypeURI = None
    form_type: TEFormsFormTypeURI = None
    place_of_performance: List[TNUTSConceptURI] = None
    legal_basis_directive: TLegalBasisConceptURI = None


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
