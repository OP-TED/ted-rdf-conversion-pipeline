from typing import List

from jinja2 import Environment, PackageLoader

from ted_sws.core.model.manifestation import SPARQLQueryResult, SPARQLTestSuiteValidationReport, \
    SHACLTestSuiteValidationReport, RDFManifestation, SPARQLQueryRefinedResultType, \
    XMLManifestationValidationSummaryReport, RDFManifestationValidationSummaryReport, XPATHCoverageSummaryReport, \
    XPATHCoverageSummaryResult, SPARQLSummaryCountReport, SHACLSummarySeverityCountReport, SPARQLSummaryResult, \
    SHACLSummaryResult, ValidationSummaryReport
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.validation_report import ReportNotice
from ted_sws.notice_transformer.adapters.notice_transformer import NoticeTransformer
from ted_sws.notice_validator.resources.templates import TEMPLATE_METADATA_KEY

TEMPLATES = Environment(loader=PackageLoader("ted_sws.notice_validator.resources", "templates"))
VALIDATION_SUMMARY_REPORT_TEMPLATE = "validation_summary_report.jinja2"

MAPPING_SUITE_IDENTIFIER = "mapping_suite_identifier"
TEST_SUITE_IDENTIFIER = "test_suite_identifier"


def find_validation_results(results: List, result: dict):
    found_results = list(filter(
        lambda record: record.mapping_suite_identifier == result[
            MAPPING_SUITE_IDENTIFIER] and record.test_suite_identifier == result[TEST_SUITE_IDENTIFIER],
        results
    ))
    return found_results


class ManifestationValidationSummaryRunner:
    notices: List[Notice]

    def __init__(self, notices: List[Notice]):
        self.notices = notices


class RDFManifestationValidationSummaryRunner(ManifestationValidationSummaryRunner):
    @classmethod
    def sparql_summary_result(cls, sparql_report: SPARQLTestSuiteValidationReport,
                              result_counts: List[SPARQLSummaryResult]) -> (bool, SPARQLSummaryResult):
        mapping_suite_id = sparql_report.mapping_suite_identifier
        test_suite_id = sparql_report.test_suite_identifier

        found_results = find_validation_results(result_counts, {MAPPING_SUITE_IDENTIFIER: mapping_suite_id,
                                                                TEST_SUITE_IDENTIFIER: test_suite_id})
        is_found: bool = found_results and len(found_results) > 0
        result_validation: SPARQLSummaryResult
        if is_found:
            result_validation = found_results[0]
        else:
            result_validation = SPARQLSummaryResult()
            result_validation.mapping_suite_identifier = sparql_report.mapping_suite_identifier
            result_validation.test_suite_identifier = sparql_report.test_suite_identifier
        return not is_found, result_validation

    def notice_sparql_summary(self, notice: Notice, report: RDFManifestationValidationSummaryReport):
        manifestation = self._manifestation(notice)
        if manifestation:
            report_count: SPARQLSummaryCountReport = report.sparql_summary.aggregate
            result_counts: List[SPARQLSummaryResult] = report.sparql_summary.validation_results
            sparql_reports: List[SPARQLTestSuiteValidationReport] = manifestation.sparql_validations
            if sparql_reports:
                for sparql_report in sparql_reports:
                    validation_results: List[SPARQLQueryResult] = sparql_report.validation_results
                    is_new, result_validation = self.sparql_summary_result(sparql_report, result_counts)
                    result_count: SPARQLSummaryCountReport = result_validation.aggregate
                    if validation_results:
                        for validation in validation_results:
                            if validation.result == SPARQLQueryRefinedResultType.VALID.value:
                                report_count.valid += 1
                                result_count.valid += 1
                            elif validation.result == SPARQLQueryRefinedResultType.UNVERIFIABLE.value:
                                report_count.unverifiable += 1
                                result_count.unverifiable += 1
                            elif validation.result == SPARQLQueryRefinedResultType.INVALID.value:
                                report_count.invalid += 1
                                result_count.invalid += 1
                            elif validation.result == SPARQLQueryRefinedResultType.WARNING.value:
                                report_count.warning += 1
                                result_count.warning += 1
                            elif validation.result == SPARQLQueryRefinedResultType.ERROR.value:
                                report_count.error += 1
                                result_count.error += 1

                    if is_new:
                        result_counts.append(result_validation)

    @classmethod
    def _manifestation(cls, notice: Notice) -> RDFManifestation:
        return notice.rdf_manifestation

    @classmethod
    def shacl_summary_result(cls, shacl_report: SHACLTestSuiteValidationReport,
                             result_counts: List[SHACLSummaryResult]) -> (bool, SHACLSummaryResult):
        mapping_suite_id = shacl_report.mapping_suite_identifier
        test_suite_id = shacl_report.test_suite_identifier
        found_results = find_validation_results(result_counts, {MAPPING_SUITE_IDENTIFIER: mapping_suite_id,
                                                                TEST_SUITE_IDENTIFIER: test_suite_id})
        is_found: bool = found_results and len(found_results) > 0
        result_validation: SHACLSummaryResult
        if is_found:
            result_validation = found_results[0]
        else:
            result_validation = SHACLSummaryResult()
            result_validation.mapping_suite_identifier = shacl_report.mapping_suite_identifier
            result_validation.test_suite_identifier = shacl_report.test_suite_identifier
        return not is_found, result_validation

    def notice_shacl_summary(self, notice: Notice, report: RDFManifestationValidationSummaryReport):
        manifestation = self._manifestation(notice)
        if manifestation:
            report_count: SHACLSummarySeverityCountReport = report.shacl_summary.result_severity.aggregate
            result_counts: List[SHACLSummaryResult] = report.shacl_summary.validation_results
            shacl_reports: List[SHACLTestSuiteValidationReport] = manifestation.shacl_validations
            if shacl_reports:
                for shacl_report in shacl_reports:
                    validation_results = shacl_report.validation_results
                    is_new, result_validation = self.shacl_summary_result(shacl_report, result_counts)
                    result_count: SHACLSummarySeverityCountReport = result_validation.result_severity.aggregate
                    if validation_results and validation_results.results_dict:
                        bindings = validation_results.results_dict['results']['bindings']
                        for binding in bindings:
                            result_severity = binding['resultSeverity']
                            if result_severity:
                                if result_severity['value'].endswith("#Violation"):
                                    report_count.violation += 1
                                    result_count.violation += 1
                                elif result_severity['value'].endswith("#Info"):
                                    report_count.info += 1
                                    result_count.info += 1
                                elif result_severity['value'].endswith("#Warning"):
                                    report_count.warning += 1
                                    result_count.warning += 1

                    if is_new:
                        result_counts.append(result_validation)

    def validation_summary(self) -> RDFManifestationValidationSummaryReport:
        notices = self.notices
        report: RDFManifestationValidationSummaryReport = RDFManifestationValidationSummaryReport()

        for notice in notices:
            self.notice_sparql_summary(notice, report)
            self.notice_shacl_summary(notice, report)

        return report


class DistilledRDFManifestationValidationSummaryRunner(RDFManifestationValidationSummaryRunner):
    @classmethod
    def _manifestation(cls, notice: Notice) -> RDFManifestation:
        return notice.distilled_rdf_manifestation


class XMLManifestationValidationSummaryRunner(ManifestationValidationSummaryRunner):
    def validation_summary(self) -> XMLManifestationValidationSummaryReport:
        notices = self.notices
        report: XMLManifestationValidationSummaryReport = XMLManifestationValidationSummaryReport()
        xpath_coverage_summary: XPATHCoverageSummaryReport = report.xpath_coverage_summary

        if len(notices) > 0:
            xml_manifestation = notices[0].xml_manifestation
            if xml_manifestation.xpath_coverage_validation:
                mapping_suite_identifier = xml_manifestation.xpath_coverage_validation.mapping_suite_identifier
                xpath_coverage_summary.mapping_suite_identifier = mapping_suite_identifier

        validation_result: XPATHCoverageSummaryResult = report.xpath_coverage_summary.validation_result
        for notice in notices:
            xpath_coverage_validation = notice.xml_manifestation.xpath_coverage_validation
            if xpath_coverage_validation:
                notice_validation_result = xpath_coverage_validation.validation_result
                validation_result.xpath_covered += len(notice_validation_result.xpath_covered)
                validation_result.xpath_not_covered += len(notice_validation_result.xpath_not_covered)

        return report


class ValidationSummaryRunner:
    """
        Runs Validation Summary
    """

    def __init__(self):
        """

        """

    @classmethod
    def validation_summary(cls, notices: List[Notice]) -> ValidationSummaryReport:
        report: ValidationSummaryReport = ValidationSummaryReport(
            object_data="ValidationSummaryReport"
        )

        xml_manifestation_runner = XMLManifestationValidationSummaryRunner(notices)
        report.xml_manifestation = xml_manifestation_runner.validation_summary()

        rdf_manifestation_runner = RDFManifestationValidationSummaryRunner(notices)
        report.rdf_manifestation = rdf_manifestation_runner.validation_summary()

        distilled_rdf_manifestation_runner = DistilledRDFManifestationValidationSummaryRunner(notices)
        report.distilled_rdf_manifestation = distilled_rdf_manifestation_runner.validation_summary()

        return report

    @classmethod
    def validation_summary_for_notice(cls, notice: Notice) -> ValidationSummaryReport:
        return cls.validation_summary([notice])

    @classmethod
    def validation_summary_for_notices(cls, notices: List[ReportNotice]) -> ValidationSummaryReport:
        report: ValidationSummaryReport = cls.validation_summary(
            sorted(NoticeTransformer.map_report_notices_to_notices(notices),
                   key=lambda notice: notice.ted_id))
        report.notices = sorted(NoticeTransformer.transform_validation_report_notices(notices, group_depth=1),
                                key=lambda report_data: report_data.notice_id)

        return report

    @classmethod
    def json_report(cls, report) -> dict:
        return report.dict()

    @classmethod
    def html_report(cls, report, metadata: dict = None) -> str:
        data: dict = cls.json_report(report)
        data[TEMPLATE_METADATA_KEY] = metadata
        return TEMPLATES.get_template(VALIDATION_SUMMARY_REPORT_TEMPLATE).render(data)
