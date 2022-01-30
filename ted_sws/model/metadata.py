#!/usr/bin/python3

# metadata.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from dataclasses import dataclass

from ted_sws.model import NoticeMetadata


@dataclass(frozen=True)
class OriginalMetadata(NoticeMetadata):
    """
        Metadata (standard forms) extracted from TED.

        When a notice is extracted from TED it is associated with metadata as currently organised by the TED website
        in accordance to StandardForms. This shall be harmonised with future eForms, Cellar CDM model and possibly
        the Legal Analysis Methodology (LAM).
    """


@dataclass(frozen=True)
class NormalisedMetadata(NoticeMetadata):
    """
        Metadata harmonised by taking into consideration standard forms, eForms, Cellar CDM model and possibly the Legal
        Analysis Methodology (LAM).
    """