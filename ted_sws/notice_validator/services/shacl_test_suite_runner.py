import json
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, PackageLoader

from ted_sws.core.model.manifestation import RDFManifestation, RDFValidationManifestation
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.transform import MappingSuite, FileResource, SHACLTestSuite
from ted_sws.data_manager.adapters.repository_abc import NoticeRepositoryABC, MappingSuiteRepositoryABC
from ted_sws.notice_validator.adapters.shacl_runner import SHACLRunner
from ted_sws.notice_validator.model.shacl_test_suite import SHACLShapeValidation, SHACLTestSuiteExecution, \
    SHACLShapeValidationResult, SHACLShapeResultReport
from ted_sws.resources import SHACL_RESULT_QUERY_PATH

TEMPLATES = Environment(loader=PackageLoader("ted_sws.notice_validator.resources", "templates"))
SHACL_TEST_SUITE_EXECUTION_HTML_REPORT_TEMPLATE = "shacl_shape_validation_results_report.jinja2"



class SHACLTestSuiteRunner:
    """

        Runs SHACL shapes tests suites .
    """

    def __init__(self, rdf_manifestation: RDFManifestation, shacl_test_suite: SHACLTestSuite,
                 mapping_suite: MappingSuite):
        self.rdf_manifestation = rdf_manifestation
        self.shacl_test_suite = shacl_test_suite
        self.mapping_suite = mapping_suite

    @classmethod
    def _shacl_shape_from_file_resource(cls, file_resource: FileResource) -> SHACLShapeValidation:
        """
        Gets file content and converts to a SHACL shape validation
        :param file_resource:
        :return:
        """
        return SHACLShapeValidation(title=file_resource.file_name, content=file_resource.file_content)

    def execute_test_suite(self) -> SHACLTestSuiteExecution:
        """
            Executing SHACL shapes validation from a SHACL test suite and return execution details
        :return:
        """
        shacl_runner = SHACLRunner(self.rdf_manifestation.object_data)
        shacl_shape_result_query = SHACL_RESULT_QUERY_PATH.read_text()
        test_suite_executions = SHACLTestSuiteExecution(mapping_suite_identifier=self.mapping_suite.identifier,
                                                        shacl_test_suite_identifier=self.shacl_test_suite.identifier,
                                                        execution_results=[],
                                                        object_data="SHACLTestSuiteExecution")
        for shacl_file_resource in self.shacl_test_suite.shacl_tests:
            shacl_shapes = self._shacl_shape_from_file_resource(file_resource=shacl_file_resource)
            shacl_shape_validation_result = SHACLShapeValidationResult(shapes=shacl_shapes)
            try:
                shacl_shape_validation_result.identifier = Path(shacl_file_resource.file_name).stem
                conforms, result_graph, results_text = shacl_runner.validate(shacl_shapes.content)
                shacl_shape_validation_result.conforms = str(conforms)
                shacl_shape_validation_result.results_dict = json.loads(result_graph.query(shacl_shape_result_query).serialize(
                    format='json').decode("UTF-8"))
            except Exception as e:
                shacl_shape_validation_result.error = str(e)
            test_suite_executions.execution_results.append(shacl_shape_validation_result)
        return test_suite_executions


class SHACLReportBuilder:
    """
        Given a SHACLShapeValidationResult, generates JSON and HTML reports.
    """

    def __init__(self, shacl_test_suite_execution: SHACLTestSuiteExecution):
        self.shacl_test_suite_execution = shacl_test_suite_execution

    def generate_json(self) -> RDFValidationManifestation:
        """
        Generating json report from SHACL test suite execution results
        :return:
        """
        return self.shacl_test_suite_execution

    def generate_html(self) -> RDFValidationManifestation:
        """
        Generating html report from SHACL test suite execution results
        :return:
        """
        report = TEMPLATES.get_template(SHACL_TEST_SUITE_EXECUTION_HTML_REPORT_TEMPLATE).render(
            self.shacl_test_suite_execution.dict())

        return RDFValidationManifestation(object_data=report)

    @classmethod
    def generate_json_for_shacl_validation_result(cls, shacl_shape_validation_result: SHACLShapeValidationResult,
                                                  mapping_suite_package: MappingSuite) -> RDFValidationManifestation:
        """
        Generating json report from single SHACL shapes test result
        :return:
        """

        sparql_result_report = SHACLShapeResultReport(
            created=datetime.now().isoformat(),
            mapping_suite_identifier=mapping_suite_package.identifier,
            validation_result=shacl_shape_validation_result,
            object_data="SHACLTestSuiteExecution"
        )

        return sparql_result_report

    @classmethod
    def generate_html_shacl_validation_result(cls, shacl_shape_validation_result: SHACLShapeValidationResult,
                                              mapping_suite_package: MappingSuite) -> RDFValidationManifestation:
        """
        Generating html report from single SHACL shapes test result
        :return:
        """
        result = SHACLTestSuiteExecution(
            shacl_test_suite_identifier=shacl_shape_validation_result.identifier,
            mapping_suite_identifier=mapping_suite_package.identifier,
            execution_results=[shacl_shape_validation_result],
            object_data="SHACLTestSuiteExecution"
        )

        data = result.dict()
        data["test_identifier_label"] = "SHACL test identifier"

        report = TEMPLATES.get_template(SHACL_TEST_SUITE_EXECUTION_HTML_REPORT_TEMPLATE).render(data)

        return RDFValidationManifestation(object_data=report)


def validate_notice_with_shacl_suite(notice: Notice, mapping_suite_package: MappingSuite):
    """
    Validates a notice with a shacl test suites
    :param notice:
    :param mapping_suite_package:
    :return:
    """
    rdf_manifestation = notice.rdf_manifestation
    shacl_test_suites = mapping_suite_package.shacl_test_suites
    for shacl_test_suite in shacl_test_suites:
        test_suite_execution = SHACLTestSuiteRunner(rdf_manifestation=rdf_manifestation,
                                                     shacl_test_suite=shacl_test_suite,
                                                     mapping_suite=mapping_suite_package).execute_test_suite()
        report_builder = SHACLReportBuilder(shacl_test_suite_execution=test_suite_execution)
        notice.set_rdf_validation(rdf_validation=report_builder.generate_json())
        notice.set_rdf_validation(rdf_validation=report_builder.generate_html())


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

