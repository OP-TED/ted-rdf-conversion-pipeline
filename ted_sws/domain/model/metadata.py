#!/usr/bin/python3

# metadata.py
# Date:  09/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from ted_sws.domain.model import PropertyBaseModel


class Metadata(PropertyBaseModel):
    """
    Unified interface for metadata
    """


class NormalizedMetadata(Metadata):
    """
    Stores notice normalized metadata
    """


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
    OC: str = None
    OJ: str = None
    OL: str = None
    OY: str = None
    PC: str = None
    PD: str = None
    PR: str = None
    RC: str = None
    RN: str = None
    RP: str = None
    TD: str = None
    TVH: str = None
    TVL: str = None
    TY: str = None
