#!/usr/bin/python3

# metadata.py
# Date:  09/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from typing import List

from deepdiff import DeepDiff

from ted_sws.domain.model import PropertyBaseModel


class Metadata(PropertyBaseModel):
    """
        Unified interface for metadata
    """


class ExtractedMetadata(Metadata):
    """
        Stores extracted metadata
    """
    title: List[str] = None
    notice_publication_number: List[str] = None
    publication_date: List[str] = None
    ojs_issue_number: List[str] = None
    city_of_buyer: List[str] = None
    name_of_buyer: List[str] = None
    original_language: List[str] = None
    country_of_buyer: List[str] = None
    type_of_buyer: List[str] = None
    eu_institution: List[str] = None
    document_sent_date: List[str] = None
    deadline_for_submission: List[str] = None
    type_of_contract: List[str] = None
    type_of_procedure: List[str] = None
    notice_type: List[str] = None
    regulation: List[str] = None
    type_of_bid: List[str] = None
    award_criteria: List[str] = None
    common_procurement: List[str] = None
    place_of_performance: List[str] = None
    internet_address: List[str] = None
    legal_basis_directive: List[str] = None


class NormalisedMetadata(Metadata):
    """
        Stores notice normalised metadata
    """
    title: List[str] = None
    notice_publication_number: List[str] = None
    publication_date: List[str] = None
    ojs_issue_number: List[str] = None
    city_of_buyer: List[str] = None
    name_of_buyer: List[str] = None
    original_language: List[str] = None
    country_of_buyer: List[str] = None
    type_of_buyer: List[str] = None
    eu_institution: List[str] = None
    document_sent_date: List[str] = None
    deadline_for_submission: List[str] = None
    type_of_contract: List[str] = None
    type_of_procedure: List[str] = None
    notice_type: List[str] = None
    regulation: List[str] = None
    type_of_bid: List[str] = None
    award_criteria: List[str] = None
    common_procurement: List[str] = None
    place_of_performance: List[str] = None
    internet_address: List[str] = None
    legal_basis_directive: List[str] = None


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
