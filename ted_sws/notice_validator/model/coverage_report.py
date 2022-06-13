#!/usr/bin/python3

import abc
from typing import List, Optional

from ted_sws.core.model import PropertyBaseModel


class XPathAssertion(PropertyBaseModel, abc.ABC):
    title: Optional[str]
    xpath: Optional[str]
    count: Optional[int]
    query_result: Optional[bool]
    required: Optional[bool]


class NoticeCoverageReport(PropertyBaseModel, abc.ABC):
    """
    """

    created_at: Optional[str]
    mapping_suite_id: Optional[str]
    notice_id: Optional[str]
    xpath_assertions: Optional[List[XPathAssertion]]
    xpath_desertions: Optional[List[str]]
