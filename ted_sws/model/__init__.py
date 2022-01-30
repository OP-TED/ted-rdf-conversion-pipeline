#!/usr/bin/python3

# __init__.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import abc
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class NoticeMetadata(dict, abc.ABC):
    """
        The metadata describe the notice through a defined set of properties.

        This can be conceptualised as a set of Key-Values, with a predefined number of keys.
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)


class NoticeStatus(Enum):
    """
        The status of the notice in the pipeline
    """
    RAW = 10
    NORMALISED_METADATA = 20
    INELIGIBLE_FOR_TRANSFORMATION = 27
    TRANSFORMED = 30
    ASSESSED_TRANSFORMATION = 40
    INELIGIBLE_FOR_PACKAGING = 45
    PACKAGED = 50
    PUBLISHED = 60
    PUBLICLY_AVAILABLE = 70
    FAULTY_PACKAGING_OR_PUBLICATION = 47  # to be investigated if more fine-grained checks can be adopted


class WorkExpression(abc.ABC):
    """
        A Merger of Work and Expression FRBR classes.
    """


class Manifestation(abc.ABC):
    """
        A manifestation that embodies a FRBR Work/Expression.
    """
    object_data: bytes  # immutable object content
