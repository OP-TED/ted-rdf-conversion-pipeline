import json
from typing import List

from jinja2 import Environment, PackageLoader

from ted_sws.core.model.manifestation import RDFManifestation, SHACLTestSuiteValidationReport, \
    QueriedSHACLShapeValidationResult
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.transform import MappingSuite, SHACLTestSuite
from ted_sws.data_manager.adapters.repository_abc import NoticeRepositoryABC, MappingSuiteRepositoryABC
from ted_sws.notice_validator.adapters.shacl_runner import SHACLRunner
from ted_sws.resources import SHACL_RESULT_QUERY_PATH


class CoverageTestSuiteRunner:
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
        except Exception as e:
            shacl_shape_validation_result.error = str(e)

        return SHACLTestSuiteValidationReport(mapping_suite_identifier=self.mapping_suite.identifier,
                                              test_suite_identifier=self.shacl_test_suite.identifier,
                                              validation_results=shacl_shape_validation_result,
                                              object_data="SHACLTestSuiteExecution")


def generate_coverage_report(shacl_test_suite_execution: SHACLTestSuiteValidationReport) -> \
        SHACLTestSuiteValidationReport:
    """
    """
    json_report = shacl_test_suite_execution.dict()
    shacl_test_suite_execution.object_data = html_report
    return shacl_test_suite_execution
