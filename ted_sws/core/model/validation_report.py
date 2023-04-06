from pathlib import Path
from typing import Optional, List

from ted_sws.core.model import PropertyBaseModel
from ted_sws.core.model.manifestation import SPARQLQueryResult, ValidationManifestation, Manifestation, SPARQLQuery
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.validation_report_data import ReportPackageNoticeData, ReportNoticeData


class ReportNoticeMetadata(PropertyBaseModel):
    path: Optional[Path]


class ReportNotice(PropertyBaseModel):
    """
    Used for processing
    """
    notice: Notice
    metadata: Optional[ReportNoticeMetadata] = ReportNoticeMetadata()


class QueryValidationSummaryCountReportStatus(PropertyBaseModel):
    count: Optional[int] = 0
    notices: Optional[List[ReportPackageNoticeData]] = []


class SPARQLValidationSummaryCountReport(PropertyBaseModel):
    valid: Optional[QueryValidationSummaryCountReportStatus] = QueryValidationSummaryCountReportStatus()
    unverifiable: Optional[QueryValidationSummaryCountReportStatus] = QueryValidationSummaryCountReportStatus()
    warning: Optional[QueryValidationSummaryCountReportStatus] = QueryValidationSummaryCountReportStatus()
    invalid: Optional[QueryValidationSummaryCountReportStatus] = QueryValidationSummaryCountReportStatus()
    error: Optional[QueryValidationSummaryCountReportStatus] = QueryValidationSummaryCountReportStatus()
    unknown: Optional[QueryValidationSummaryCountReportStatus] = QueryValidationSummaryCountReportStatus()


class SPARQLSummaryQuery(PropertyBaseModel):
    """
    Stores SPARQL query details
    """
    title: Optional[str]
    query: str


class SPARQLValidationSummaryQueryResult(PropertyBaseModel):
    """

    """
    query: SPARQLSummaryQuery
    identifier: Optional[str]
    aggregate: Optional[SPARQLValidationSummaryCountReport] = SPARQLValidationSummaryCountReport()
    test_suite_identifier: Optional[str]


class SPARQLValidationSummaryReport(ValidationManifestation):
    notices: Optional[List[ReportNoticeData]] = []
    mapping_suite_ids: Optional[List[str]] = []
    test_suite_ids: Optional[List[str]] = []
    validation_results: Optional[List[SPARQLValidationSummaryQueryResult]] = []


class SHACLSummaryQuery(PropertyBaseModel):
    """
    Stores SPARQL query details
    """
    result_path: Optional[str]


class SHACLValidationSummarySeverityCountResult(PropertyBaseModel):
    info: Optional[QueryValidationSummaryCountReportStatus] = QueryValidationSummaryCountReportStatus()
    warning: Optional[QueryValidationSummaryCountReportStatus] = QueryValidationSummaryCountReportStatus()
    violation: Optional[QueryValidationSummaryCountReportStatus] = QueryValidationSummaryCountReportStatus()


class SHACLValidationSummaryResult(PropertyBaseModel):
    query: Optional[SHACLSummaryQuery] = SHACLSummaryQuery()
    result_severity: Optional[SHACLValidationSummarySeverityCountResult] = SHACLValidationSummarySeverityCountResult()
    conforms: Optional[QueryValidationSummaryCountReportStatus] = QueryValidationSummaryCountReportStatus()
    test_suite_identifier: Optional[str]


class SHACLValidationSummaryReport(ValidationManifestation):
    notices: Optional[List[ReportNoticeData]] = []
    mapping_suite_ids: Optional[List[str]] = []
    test_suite_ids: Optional[List[str]] = []
    validation_results: Optional[List[SHACLValidationSummaryResult]] = []
