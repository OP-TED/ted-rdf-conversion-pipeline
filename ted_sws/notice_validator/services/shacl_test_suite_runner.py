import json
from typing import List

from jinja2 import Environment, PackageLoader

from ted_sws.core.model.manifestation import RDFManifestation
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.transform import MappingSuite, SHACLTestSuite
from ted_sws.data_manager.adapters.repository_abc import NoticeRepositoryABC, MappingSuiteRepositoryABC
from ted_sws.notice_validator.adapters.shacl_runner import SHACLRunner
from ted_sws.notice_validator.model.shacl_test_suite import QueriedSHACLShapeValidationResult, \
    SHACLSuiteValidationReport
from ted_sws.resources import SHACL_RESULT_QUERY_PATH

TEMPLATES = Environment(loader=PackageLoader("ted_sws.notice_validator.resources", "templates"))
SHACL_TEST_SUITE_EXECUTION_HTML_REPORT_TEMPLATE = "shacl_shape_validation_results_report.jinja2"


class SHACLTestSuiteRunner:
    """

        Runs SHACL shape tests suites .
    """

    def __init__(self, rdf_manifestation: RDFManifestation, shacl_test_suite: SHACLTestSuite,
                 mapping_suite: MappingSuite):
        self.rdf_manifestation = rdf_manifestation
        self.shacl_test_suite = shacl_test_suite
        self.mapping_suite = mapping_suite

    def execute_test_suite(self) -> SHACLSuiteValidationReport:
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
        except Exception as e:
            shacl_shape_validation_result.error = str(e)

        return SHACLSuiteValidationReport(mapping_suite_identifier=self.mapping_suite.identifier,
                                          shacl_test_suite_identifier=self.shacl_test_suite.identifier,
                                          validation_result=shacl_shape_validation_result,
                                          object_data="SHACLTestSuiteExecution")


class SHACLReportBuilder:
    """
        Given a QueriedSHACLShapeValidationResult, generates JSON and HTML reports.
    """

    def __init__(self, shacl_test_suite_execution: SHACLSuiteValidationReport):
        self.shacl_test_suite_execution = shacl_test_suite_execution

    def generate_report(self) -> SHACLSuiteValidationReport:
        html_report = TEMPLATES.get_template(SHACL_TEST_SUITE_EXECUTION_HTML_REPORT_TEMPLATE).render(
            self.shacl_test_suite_execution.dict())
        self.shacl_test_suite_execution.object_data = html_report
        return self.shacl_test_suite_execution


def validate_notice_with_shacl_suite(notice: Notice, mapping_suite_package: MappingSuite):
    """
    Validates a notice with a shacl test suites
    :param notice:
    :param mapping_suite_package:
    :return:
    """

    def shacl_validation(rdf_manifestation: RDFManifestation) -> List[SHACLSuiteValidationReport]:
        reports = []
        shacl_test_suites = mapping_suite_package.shacl_test_suites
        for shacl_test_suite in shacl_test_suites:
            test_suite_execution = SHACLTestSuiteRunner(rdf_manifestation=rdf_manifestation,
                                                        shacl_test_suite=shacl_test_suite,
                                                        mapping_suite=mapping_suite_package).execute_test_suite()
            report_builder = SHACLReportBuilder(shacl_test_suite_execution=test_suite_execution)
            reports.append(report_builder.generate_report())

        return reports

    for report in shacl_validation(rdf_manifestation=notice.rdf_manifestation):
        notice.set_rdf_validation(rdf_validation=report)

    for report in shacl_validation(rdf_manifestation=notice.distilled_rdf_manifestation):
        notice.set_distilled_rdf_validation(rdf_validation=report)


def validate_notice_by_id_with_shacl_suite(notice_id: str, mapping_suite_identifier: str,
                                           notice_repository: NoticeRepositoryABC,
                                           mapping_suite_repository: MappingSuiteRepositoryABC):
    """
    Validates a notice by id with a shacl test suites
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
    validate_notice_with_shacl_suite(notice=notice, mapping_suite_package=mapping_suite_package)
    notice_repository.update(notice=notice)
