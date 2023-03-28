import json
import logging
from typing import List, Union

from jinja2 import Environment, PackageLoader

from ted_sws.core.model.manifestation import RDFManifestation, SHACLTestSuiteValidationReport, \
    QueriedSHACLShapeValidationResult
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.transform import MappingSuite, SHACLTestSuite
from ted_sws.core.model.validation_report import ReportNotice, SHACLValidationSummaryReport, \
    SHACLValidationSummaryResult, SHACLSummaryQuery
from ted_sws.core.model.validation_report_data import ReportPackageNoticeData
from ted_sws.data_manager.adapters.repository_abc import NoticeRepositoryABC, MappingSuiteRepositoryABC
from ted_sws.notice_transformer.adapters.notice_transformer import NoticeTransformer
from ted_sws.notice_validator.adapters.shacl_runner import SHACLRunner
from ted_sws.notice_validator.resources.templates import TEMPLATE_METADATA_KEY
from ted_sws.resources import SHACL_RESULT_QUERY_PATH
from ted_sws.notice_validator.services import NOTICE_IDS_FIELD

TEMPLATES = Environment(loader=PackageLoader("ted_sws.notice_validator.resources", "templates"))
SHACL_TEST_SUITE_EXECUTION_HTML_REPORT_TEMPLATE = "shacl_shape_validation_results_report.jinja2"
SHACL_SUMMARY_HTML_REPORT_TEMPLATE = "shacl_summary_report.jinja2"


class SHACLTestSuiteRunner:
    """

        Runs SHACL shape tests suites .
    """

    def __init__(self, rdf_manifestation: RDFManifestation, shacl_test_suite: SHACLTestSuite,
                 mapping_suite: MappingSuite):
        self.rdf_manifestation = rdf_manifestation
        self.shacl_test_suite = shacl_test_suite
        self.mapping_suite = mapping_suite

    def execute_test_suite(self) -> SHACLTestSuiteValidationReport:
        """
            Executing SHACL shape validation from a SHACL test suite and return execution details
        :return:
        """
        shacl_runner = SHACLRunner(self.rdf_manifestation.object_data)
        shacl_shape_result_query = SHACL_RESULT_QUERY_PATH.read_text()
        shacl_shape_validation_result = QueriedSHACLShapeValidationResult()
        try:
            shacl_shape_validation_result.identifier = self.shacl_test_suite.identifier
            conforms, result_graph, results_text = shacl_runner.validate(self.shacl_test_suite.shacl_tests)
            shacl_shape_validation_result.conforms = str(conforms)
            shacl_shape_validation_result.results_dict = json.loads(
                result_graph.query(shacl_shape_result_query).serialize(
                    format='json').decode("UTF-8"))

            if (shacl_shape_validation_result.results_dict
                    and shacl_shape_validation_result.results_dict["results"]
                    and shacl_shape_validation_result.results_dict["results"]["bindings"]):
                shacl_shape_validation_result.results_dict["results"]["bindings"].sort(
                    key=lambda x: x["focusNode"]["value"])

        except Exception as e:
            shacl_shape_validation_result.error = str(e)[:100]

        return SHACLTestSuiteValidationReport(mapping_suite_identifier=self.mapping_suite.get_mongodb_id(),
                                              test_suite_identifier=self.shacl_test_suite.identifier,
                                              validation_results=shacl_shape_validation_result,
                                              object_data="SHACLTestSuiteExecution")


def generate_shacl_report(shacl_test_suite_execution: SHACLTestSuiteValidationReport,
                          notice_ids: List[str] = None, with_html: bool = False) -> SHACLTestSuiteValidationReport:
    """
        This function generate html report after SHACL test execution.
    :param with_html: generate HTML report
    :param notice_ids:
    :param shacl_test_suite_execution:
    :return:
    """
    if with_html:
        template_data: dict = shacl_test_suite_execution.dict()
        template_data[NOTICE_IDS_FIELD] = notice_ids
        html_report = TEMPLATES.get_template(SHACL_TEST_SUITE_EXECUTION_HTML_REPORT_TEMPLATE).render(template_data)
        shacl_test_suite_execution.object_data = html_report
    return shacl_test_suite_execution


def generate_shacl_validation_summary_report(report_notices: List[ReportNotice], mapping_suite_package: MappingSuite,
                                             execute_full_validation: bool = True,
                                             with_html: bool = False,
                                             report: SHACLValidationSummaryReport = None,
                                             metadata: dict = None) -> SHACLValidationSummaryReport:
    if report is None:
        report: SHACLValidationSummaryReport = SHACLValidationSummaryReport(
            object_data="SHACLValidationSummaryReport",
            notices=[],
            validation_results=[]
        )
    report.notices = sorted(NoticeTransformer.transform_validation_report_notices(report_notices, group_depth=1) + (
            report.notices or []), key=lambda report_data: report_data.notice_id)

    for report_notice in report_notices:
        notice = report_notice.notice
        validate_notice_with_shacl_suite(
            notice=notice,
            mapping_suite_package=mapping_suite_package,
            execute_full_validation=execute_full_validation,
            with_html=False
        )
        for shacl_validation in notice.rdf_manifestation.shacl_validations:
            test_suite_id = shacl_validation.test_suite_identifier
            report.test_suite_ids.append(test_suite_id)
            mapping_suite_versioned_id = shacl_validation.mapping_suite_identifier
            report.mapping_suite_ids.append(mapping_suite_versioned_id)

            validation: QueriedSHACLShapeValidationResult = shacl_validation.validation_results
            validation_query_result: SHACLValidationSummaryResult

            bindings = []
            if validation.results_dict:
                bindings = validation.results_dict['results']['bindings']

            is_conforms_set: bool = False
            for binding in bindings:
                result_path = binding['resultPath']['value'] if binding['resultPath'] else None
                found_validation_query_result = list(filter(
                    lambda record:
                    (record.test_suite_identifier == test_suite_id)
                    and ((record.query.result_path == result_path) if result_path else True),
                    report.validation_results
                ))

                if found_validation_query_result:
                    validation_query_result = found_validation_query_result[0]
                else:
                    validation_query_result = SHACLValidationSummaryResult(
                        test_suite_identifier=test_suite_id,
                        query=SHACLSummaryQuery(result_path=result_path)
                    )

                notice_data: ReportPackageNoticeData = ReportPackageNoticeData(
                    notice_id=notice.ted_id,
                    path=str(report_notice.metadata.path),
                    mapping_suite_versioned_id=mapping_suite_versioned_id,
                    mapping_suite_identifier=mapping_suite_package.identifier
                )
                if not is_conforms_set and validation.conforms == 'True':
                    validation_query_result.conforms.count += 1
                    validation_query_result.conforms.notices.append(notice_data)
                    is_conforms_set = True

                result_severity = binding['resultSeverity']
                if result_severity:
                    if result_severity['value'].endswith("#Violation"):
                        validation_query_result.result_severity.violation.count += 1
                        validation_query_result.result_severity.violation.notices.append(notice_data)
                    elif result_severity['value'].endswith("#Info"):
                        validation_query_result.result_severity.info.count += 1
                        validation_query_result.result_severity.info.notices.append(notice_data)
                    elif result_severity['value'].endswith("#Warning"):
                        validation_query_result.result_severity.warning.count += 1
                        validation_query_result.result_severity.warning.notices.append(notice_data)

                if not found_validation_query_result:
                    report.validation_results.append(validation_query_result)

    report.test_suite_ids = list(set(report.test_suite_ids))
    report.mapping_suite_ids = list(set(report.mapping_suite_ids))

    if with_html:
        template_data: dict = report.dict()
        template_data[TEMPLATE_METADATA_KEY] = metadata
        html_report = TEMPLATES.get_template(SHACL_SUMMARY_HTML_REPORT_TEMPLATE).render(template_data)
        report.object_data = html_report

    return report


def validate_notice_with_shacl_suite(notice: Notice, mapping_suite_package: MappingSuite,
                                     execute_full_validation: bool = True, with_html: bool = False) -> Notice:
    """
    Validates a notice with a shacl test suites
    :param with_html: generate HTML report
    :param notice:
    :param mapping_suite_package:
    :param execute_full_validation:
    :return:
    """

    def shacl_validation(notice_item: Notice, rdf_manifestation: RDFManifestation, with_html: bool = False) \
            -> List[SHACLTestSuiteValidationReport]:
        reports = []
        shacl_test_suites = mapping_suite_package.shacl_test_suites
        for shacl_test_suite in shacl_test_suites:
            test_suite_execution = SHACLTestSuiteRunner(rdf_manifestation=rdf_manifestation,
                                                        shacl_test_suite=shacl_test_suite,
                                                        mapping_suite=mapping_suite_package).execute_test_suite()
            reports.append(generate_shacl_report(shacl_test_suite_execution=test_suite_execution,
                                                 notice_ids=[notice_item.ted_id], with_html=with_html))

        return sorted(reports, key=lambda x: x.test_suite_identifier)

    if execute_full_validation:
        for report in shacl_validation(notice_item=notice, rdf_manifestation=notice.rdf_manifestation,
                                       with_html=with_html):
            notice.set_rdf_validation(rdf_validation=report)

    for report in shacl_validation(notice_item=notice, rdf_manifestation=notice.distilled_rdf_manifestation,
                                   with_html=with_html):
        notice.set_distilled_rdf_validation(rdf_validation=report)

    return notice


def validate_notice_by_id_with_shacl_suite(notice_id: str, mapping_suite_identifier: str,
                                           notice_repository: NoticeRepositoryABC,
                                           mapping_suite_repository: MappingSuiteRepositoryABC,
                                           with_html: bool = False):
    """
    Validates a notice by id with a shacl test suites
    :param with_html: generate HTML report
    :param notice_id:
    :param mapping_suite_identifier:
    :param notice_repository:
    :param mapping_suite_repository:
    :return:
    """
    notice = notice_repository.get(reference=notice_id)
    if notice is None:
        raise ValueError(f'Notice, with {notice_id} id, was not found')

    mapping_suite_package = mapping_suite_repository.get(reference=mapping_suite_identifier)
    if mapping_suite_package is None:
        raise ValueError(f'Mapping suite package, with {mapping_suite_identifier} id, was not found')
    validate_notice_with_shacl_suite(notice=notice, mapping_suite_package=mapping_suite_package, with_html=with_html)
    notice_repository.update(notice=notice)
