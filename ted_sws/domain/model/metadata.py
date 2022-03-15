#!/usr/bin/python3

# metadata.py
# Date:  09/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from typing import List

from ted_sws.domain.model import PropertyBaseModel


class Metadata(PropertyBaseModel):
    """
        Unified interface for metadata
    """
    class Config:
        underscore_attrs_are_private = True


class NormalisedMetadata(Metadata):
    """
        Stores notice normalised metadata
        TODO: This structure/set of metadata will might change in the future
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
