#!/usr/bin/python3

# __init__.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import abc
import mimetypes
from dataclasses import dataclass
from enum import Enum
from schematics.models import Model
from schematics.types import DictType, StringType


class NoticeStatus(Enum):
    """
    The status of the notice in the pipeline
    """
    RAW = 10
    NORMALISED_METADATA = 20
    INELIGIBLE_FOR_TRANSFORMATION = 23  # backlog status
    ELIGIBLE_FOR_TRANSFORMATION = 27  # forward status
    TRANSFORMED = 30
    VALIDATED_TRANSFORMATION = 40
    INELIGIBLE_FOR_PACKAGING = 43  # backlog status
    ELIGIBLE_FOR_PACKAGING = 47  # forward status
    PACKAGED = 50
    FAULTY_PACKAGE = 53  # backlog status
    CORRECT_PACKAGE = 57  # forward status
    PUBLISHED = 60
    PUBLICLY_UNAVAILABLE = 63  # to be investigated if more fine-grained checks can be adopted
    PUBLICLY_AVAILABLE = 67  # forward status


class ManifestationMimeType(Enum):
    """
    MIME types for manifestations used in this application
    """
    METS = "application/zip"
    XML = "application/xml"
    RDF = "application/rdf+xml"
    TURTLE = "text/turtle"


class WorkExpression(Model):
    """
        A Merger of Work and Expression FRBR classes.
    """


class Manifestation(Model):
    """
        A manifestation that embodies a FRBR Work/Expression.
    """
    _object_data = StringType(required=True, default="", serialized_name="object_data")  # immutable object content

    @property
    def object_data(self):
        return self._object_data

    @object_data.setter
    def object_data(self):
        raise PermissionError("Field is immutable")

    @classmethod
    def new(cls, object_data):
        result = cls()
        result._object_data = object_data
        return result

    def __str__(self):
        STR_LEN = 150  # constant
        return f"/{str(self._object_data)[:STR_LEN]}" + ("..." if len(self._object_data) > STR_LEN else "") + "/"
