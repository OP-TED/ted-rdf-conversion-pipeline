#!/usr/bin/python3

# manifestation.py
# Date:  03/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from ted_sws.domain.model import Manifestation


class METSManifestation(Manifestation):
    """

    """


class RDFManifestation(Manifestation):
    """
        Transformed manifestation in RDF format
    """


class XMLManifestation(Manifestation):
    """
        Original XML Notice manifestation as published on the TED website.
    """

    def __init__(self, object_data: bytes):
        self.objectData = object_data