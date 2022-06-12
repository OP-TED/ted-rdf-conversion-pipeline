import re
from pathlib import Path
from typing import Tuple, List

from jinja2 import Environment, PackageLoader

from ted_sws.core.model.manifestation import RDFManifestation, SPARQLQueryResult, \
    SPARQLTestSuiteValidationReport, SPARQLQuery
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.transform import SPARQLTestSuite, MappingSuite, FileResource
from ted_sws.data_manager.adapters.repository_abc import NoticeRepositoryABC, MappingSuiteRepositoryABC
from ted_sws.notice_validator.adapters.sparql_runner import SPARQLRunner

TEMPLATES = Environment(loader=PackageLoader("ted_sws.notice_validator.resources", "templates"))
SPARQL_TEST_SUITE_EXECUTION_HTML_REPORT_TEMPLATE = "sparql_query_results_report.jinja2"

QUERY_METADATA_TITLE = "title"
QUERY_METADATA_DESCRIPTION = "description"
DEFAULT_QUERY_TITLE = "untitled query"
DEFAULT_QUERY_DESCRIPTION = "un-described query"


class SPARQLTestSuiteRunner:
    """

        One of the assumptions is that all the SPARQL queries are of type ASK.
    """

    def __init__(self, rdf_manifestation: RDFManifestation, sparql_test_suite: SPARQLTestSuite,
                 mapping_suite: MappingSuite):
        self.rdf_manifestation = rdf_manifestation
        self.sparql_test_suite = sparql_test_suite
        self.mapping_suite = mapping_suite

    @classmethod
    def _sanitize_query(cls, query: str) -> str:
        query = re.sub(r'(?m)^ *#.*\n?', '', query).strip('\n ')
        return query

    @classmethod
    def _sparql_query_from_file_resource(cls, file_resource: FileResource) -> SPARQLQuery:
        """
        Gets file content and converts to a SPARQLQuery
        :param file_resource:
        :return:
        """
        metadata = extract_metadata_from_sparql_query(file_resource.file_content)
        title = metadata[QUERY_METADATA_TITLE] \
            if QUERY_METADATA_TITLE in metadata else DEFAULT_QUERY_TITLE
        description = metadata[QUERY_METADATA_DESCRIPTION] \
            if QUERY_METADATA_DESCRIPTION in metadata else DEFAULT_QUERY_DESCRIPTION
        query = cls._sanitize_query(file_resource.file_content)
        return SPARQLQuery(title=title, description=description, query=query)

    def execute_test_suite(self) -> SPARQLTestSuiteValidationReport:
        """
            Executing SPARQL queries from a SPARQL test suite and return execution details
        :return:
        """
        sparql_runner = SPARQLRunner(self.rdf_manifestation.object_data)
        test_suite_executions = SPARQLTestSuiteValidationReport(mapping_suite_identifier=self.mapping_suite.identifier,
                                                                test_suite_identifier=self.sparql_test_suite.identifier,
                                                                validation_results=[],
                                                                object_data="SPARQLTestSuiteExecution")
        for query_file_resource in self.sparql_test_suite.sparql_tests:
            sparql_query = self._sparql_query_from_file_resource(file_resource=query_file_resource)
            sparql_query_result = SPARQLQueryResult(query=sparql_query)
            try:
                sparql_query_result.identifier = Path(query_file_resource.file_name).stem
                query_result = sparql_runner.query(sparql_query.query)
                sparql_query_result.result = str(
                    query_result.askAnswer) if query_result.type == "ASK" else query_result.serialize(
                    format="json")
            except Exception as e:
                sparql_query_result.error = str(e)[:100]
            test_suite_executions.validation_results.append(sparql_query_result)
        return test_suite_executions


class SPARQLReportBuilder:
    """
        Given a SPARQLQueryResult, generates JSON and HTML reports.
    """

    def __init__(self, sparql_test_suite_execution: SPARQLTestSuiteValidationReport):
        self.sparql_test_suite_execution = sparql_test_suite_execution

    def generate_report(self) -> SPARQLTestSuiteValidationReport:
        html_report = TEMPLATES.get_template(SPARQL_TEST_SUITE_EXECUTION_HTML_REPORT_TEMPLATE).render(
            self.sparql_test_suite_execution.dict())
        self.sparql_test_suite_execution.object_data = html_report
        return self.sparql_test_suite_execution


def validate_notice_with_sparql_suite(notice: Notice, mapping_suite_package: MappingSuite):
    """
    Validates a notice with a sparql test suites
    :param notice:
    :param mapping_suite_package:
    :return:
    """

    def sparql_validation(rdf_manifestation: RDFManifestation) -> List[SPARQLTestSuiteValidationReport]:
        sparql_test_suites = mapping_suite_package.sparql_test_suites
        reports = []
        for sparql_test_suite in sparql_test_suites:
            test_suite_execution = SPARQLTestSuiteRunner(rdf_manifestation=rdf_manifestation,
                                                         sparql_test_suite=sparql_test_suite,
                                                         mapping_suite=mapping_suite_package).execute_test_suite()
            report_builder = SPARQLReportBuilder(sparql_test_suite_execution=test_suite_execution)
            reports.append(report_builder.generate_report())
        return reports

    for report in sparql_validation(rdf_manifestation=notice.rdf_manifestation):
        notice.set_rdf_validation(rdf_validation=report)

    for report in sparql_validation(rdf_manifestation=notice.distilled_rdf_manifestation):
        notice.set_distilled_rdf_validation(rdf_validation=report)


def validate_notice_by_id_with_sparql_suite(notice_id: str, mapping_suite_identifier: str,
                                            notice_repository: NoticeRepositoryABC,
                                            mapping_suite_repository: MappingSuiteRepositoryABC):
    """
    Validates a notice by id with a sparql test suites
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
    validate_notice_with_sparql_suite(notice=notice, mapping_suite_package=mapping_suite_package)
    notice_repository.update(notice=notice)


def extract_metadata_from_sparql_query(content) -> dict:
    """
        Extracts a dictionary of metadata from a SPARQL query
    """

    def _process_line(line) -> Tuple[str, str]:
        if ":" in line:
            key_part, value_part = line.split(":", 1)
            key_part = key_part.replace("#", "").strip()
            value_part = value_part.strip()
            return key_part, value_part

    content_lines_with_comments = filter(lambda x: x.strip().startswith("#"), content.splitlines())
    return dict([_process_line(line) for line in content_lines_with_comments])
