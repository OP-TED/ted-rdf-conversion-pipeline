#!/usr/bin/python3

# __init__.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import abc
from dataclasses import dataclass
from enum import Enum


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



@dataclass(frozen=True)
class NoticeMetadata(dict, abc.ABC):
    """
        The metadata describe the notice through a defined set of properties.

        This can be conceptualised as a set of Key-Values, with a predefined number of keys.
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)


class WorkExpression(abc.ABC):
    """
        A Merger of Work and Expression FRBR classes.
    """


class Manifestation(abc.ABC):
    """
        A manifestation that embodies a FRBR Work/Expression.
    """
    object_data: bytes  # immutable object content
