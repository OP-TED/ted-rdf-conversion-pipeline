#!/usr/bin/python3

from typing import List, Optional, Dict

from ted_sws.core.model import PropertyBaseModel


class XPathCoverageAssertion(PropertyBaseModel):
    title: Optional[str]
    xpath: Optional[str]
    count: Optional[int]
    notice_hit: Optional[Dict[str, int]]
    query_result: Optional[bool]


class XPATHCoverageReport(PropertyBaseModel):
    """
    This is the model structure for Notice(s) XPATHs Coverage Report
    """

    created_at: Optional[str]
    mapping_suite_id: Optional[str]
    notice_id: Optional[List[str]]
    xpath_assertions: Optional[List[XPathCoverageAssertion]]
    xpath_covered: Optional[List[str]]
    xpath_not_covered: Optional[List[str]]
    xpath_extra: Optional[List[str]]
    coverage: Optional[float]
    conceptual_coverage: Optional[float]
