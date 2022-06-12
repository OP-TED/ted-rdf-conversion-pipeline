#!/usr/bin/python3

from ted_sws.core.model import PropertyBaseModel
import abc
from typing import List


class XPathAssertion(PropertyBaseModel, abc.ABC):
    title: str
    xpath: str
    count: int
    query_result: str
    required: bool


class NoticeCoverageReport(PropertyBaseModel, abc.ABC):
    """
    """

    created_at: str
    mapping_suite_id: str
    xpath_assertions: List[XPathAssertion]
