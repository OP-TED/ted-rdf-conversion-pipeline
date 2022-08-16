from typing import List

from jinja2 import Environment, PackageLoader

from ted_sws.core.model.manifestation import ValidationSummaryReport, XMLManifestationValidationSummaryReport, \
    RDFManifestationValidationSummaryReport, XPATHCoverageSummaryReport, XPATHCoverageSummaryResult, \
    SPARQLSummaryCountReport, SHACLSummarySeverityCountReport, SPARQLQueryResult, SPARQLTestSuiteValidationReport, \
    SHACLTestSuiteValidationReport, RDFManifestation, SPARQLSummaryResult, SHACLSummaryResult
from ted_sws.core.model.notice import Notice

TEMPLATES = Environment(loader=PackageLoader("ted_sws.notice_validator.resources", "templates"))
VALIDATION_SUMMARY_REPORT_TEMPLATE = "validation_summary_report.jinja2"


class ManifestationValidationSummaryRunner:
    notices: List[Notice]

    def __init__(self, notices: List[Notice]):
        self.notices = notices


class RDFManifestationValidationSummaryRunner(ManifestationValidationSummaryRunner):
    @classmethod
    def notice_sparql_summary(cls, notice: Notice, report: RDFManifestationValidationSummaryReport):
        manifestation = cls._manifestation(notice)
        if manifestation:
            report_count: SPARQLSummaryCountReport = report.sparql_summary.aggregate
            result_counts: List[SPARQLSummaryResult] = report.sparql_summary.validation_results
            sparql_reports: List[SPARQLTestSuiteValidationReport] = manifestation.sparql_validations
            if sparql_reports:
                for sparql_report in sparql_reports:
                    validation_results: List[SPARQLQueryResult] = sparql_report.validation_results
                    result_validation: SPARQLSummaryResult = SPARQLSummaryResult()
                    result_validation.mapping_suite_identifier = sparql_report.mapping_suite_identifier
                    result_validation.test_suite_identifier = sparql_report.test_suite_identifier
                    result_count: SPARQLSummaryCountReport = result_validation.aggregate
                    if validation_results:
                        for validation in validation_results:
                            if validation.result == 'True':
                                report_count.success += 1
                                result_count.success += 1
                            else:
                                report_count.fail += 1
                                result_count.fail += 1
                            if validation.error:
                                report_count.error += 1
                                result_count.error += 1

                    result_counts.append(result_validation)

    @classmethod
    def _manifestation(cls, notice: Notice) -> RDFManifestation:
        return notice.rdf_manifestation

    @classmethod
    def notice_shacl_summary(cls, notice: Notice, report: RDFManifestationValidationSummaryReport):
        manifestation = cls._manifestation(notice)
        if manifestation:
            report_count: SHACLSummarySeverityCountReport = report.shacl_summary.result_severity.aggregate
            result_counts: List[SHACLSummaryResult] = report.shacl_summary.validation_results
            shacl_reports: List[SHACLTestSuiteValidationReport] = manifestation.shacl_validations
            if shacl_reports:
                for shacl_report in shacl_reports:
                    validation_results = shacl_report.validation_results
                    result_validation: SHACLSummaryResult = SHACLSummaryResult()
                    result_validation.mapping_suite_identifier = shacl_report.mapping_suite_identifier
                    result_validation.test_suite_identifier = shacl_report.test_suite_identifier
                    result_count: SHACLSummarySeverityCountReport = result_validation.result_severity.aggregate
                    if validation_results:
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

        mapping_suite_identifier = notices[0].xml_manifestation.xpath_coverage_validation.mapping_suite_identifier
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
        pass

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
    def json_report(cls, report: ValidationSummaryReport) -> dict:
        return report.dict()

    @classmethod
    def html_report(cls, report: ValidationSummaryReport) -> str:
        data: dict = cls.json_report(report)
        html_report = TEMPLATES.get_template(VALIDATION_SUMMARY_REPORT_TEMPLATE).render(data)
        return html_report
