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


class NormalisedMetadata(Metadata):
    """
        Stores notice normalised metadata
    """
    title: str = ""


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


class ExtractedTEDMetadata(Metadata):
    """
        Stores extracted metadata
    """
    title: str = None
    notice_publication_number: str = None
    publication_date: str = None
    ojs_issue_number: str = None
    city_of_buyer: str = None
    name_of_buyer: str = None
    original_language: str = None
    country_of_buyer: str = None
    type_of_buyer: str = None
    eu_institution: str = None
    document_sent_date: str = None
    deadline_for_submission: str = None
    type_of_contract: str = None
    type_of_procedure: str = None
    notice_type: str = None
    regulation: str = None
    type_of_bid: str = None
    award_criteria: str = None
    common_procurement: str = None
    place_of_performance: str = None
    internet_address: str = None
    legal_basis_directive: str = None
