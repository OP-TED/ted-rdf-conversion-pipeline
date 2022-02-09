#!/usr/bin/python3

# manifestation.py
# Date:  03/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from enum import Enum

from pydantic import BaseModel, Field

class ManifestationMimeType(Enum):
    """
    MIME types for manifestations used in this application
    """
    METS = "application/zip"
    XML = "application/xml"
    RDF = "application/rdf+xml"
    TURTLE = "text/turtle"


class Manifestation(BaseModel):
    """
        A manifestation that embodies a FRBR Work/Expression.
    """

    class Config:
        validate_assignment = True
        orm_mode = True

    object_data: str = Field(..., allow_mutation=False)

    def __str__(self):
        STR_LEN = 150  # constant
        content = self.object_data if self.object_data else ""
        return f"/{str(content)[:STR_LEN]}" + ("..." if len(content) > STR_LEN else "") + "/"


class XMLManifestation(Manifestation):
    """
        Original XML Notice manifestation as published on the TED website.
    """


class METSManifestation(Manifestation):
    """

    """


class RDFManifestation(Manifestation):
    """
        Transformed manifestation in RDF format
    """
