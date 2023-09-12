#!/usr/bin/python3

# metadata.py
# Date:  09/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from typing import List, Optional, NamedTuple

from pydantic import Field

from ted_sws.core.model import PropertyBaseModel


class Metadata(PropertyBaseModel):
    """
        Unified interface for metadata
    """

    class Config:
        underscore_attrs_are_private = True


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
    xsd_version: str
    published_in_cellar_counter: int = Field(default=0)


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
    xsd_version: str
    published_in_cellar_counter: int = Field(default=0)



class TEDMetadata(Metadata):
    """
        Stores notice original metadata
    """
    AA: Optional[List[str]] = None
    AC: Optional[str] = None
    CY: Optional[List[str]] = None
    DD: Optional[str] = None
    DI: Optional[str] = None
    DS: Optional[str] = None
    DT: Optional[List[str]] = None
    MA: Optional[List[str]] = None
    NC: Optional[List[str]] = None
    ND: Optional[str] = None
    NL: Optional[str] = None
    OC: Optional[List[str]] = None
    OJ: Optional[str] = None
    OL: Optional[str] = None
    OY: Optional[List[str]] = None
    PC: Optional[List[str]] = None
    PD: Optional[str] = None
    PR: Optional[str] = None
    RC: Optional[List[str]] = None
    RN: Optional[List[int]] = None #TODO check if this is a list of strings, now we change to list of ints to fix errors
    RP: Optional[str] = None
    TD: Optional[str] = None
    TVH: Optional[str] = None
    TVL: Optional[str] = None
    TY: Optional[str] = None
    award_criterion_type: Optional[str] = Field(default=None, alias='award-criterion-type')
    corporate_body: List[str] = Field(default=None, alias='corporate-body')
    funding: Optional[List[str]] = None
    notice_identifier: Optional[str] = Field(default=None, alias='notice-identifier')
    notice_type: Optional[str] = Field(default=None, alias='notice-type')
    notice_version: Optional[str] = Field(default=None, alias='notice-version')
