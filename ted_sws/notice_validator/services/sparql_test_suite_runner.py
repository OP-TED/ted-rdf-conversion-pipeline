import re
from pathlib import Path
from typing import Tuple, List

from jinja2 import Environment, PackageLoader

from ted_sws.core.model.manifestation import RDFManifestation, SPARQLQueryResult, \
    SPARQLTestSuiteValidationReport, SPARQLQuery, XMLManifestation, SPARQLQueryRefinedResultType
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.transform import SPARQLTestSuite, MappingSuite, FileResource
from ted_sws.core.model.validation_report import SPARQLValidationSummaryReport, SPARQLValidationSummaryQueryResult, \
    ReportNotice
from ted_sws.core.model.validation_report_data import ReportPackageNoticeData
from ted_sws.data_manager.adapters.repository_abc import NoticeRepositoryABC, MappingSuiteRepositoryABC
from ted_sws.mapping_suite_processor.services.conceptual_mapping_generate_sparql_queries import SPARQL_XPATH_SEPARATOR
from ted_sws.notice_transformer.adapters.notice_transformer import NoticeTransformer
from ted_sws.notice_validator.adapters.sparql_runner import SPARQLRunner
from ted_sws.notice_validator.resources.templates import TEMPLATE_METADATA_KEY
from ted_sws.notice_validator.services import NOTICE_IDS_FIELD

TEMPLATES = Environment(loader=PackageLoader("ted_sws.notice_validator.resources", "templates"))
SPARQL_TEST_SUITE_EXECUTION_HTML_REPORT_TEMPLATE = "sparql_query_results_report.jinja2"
SPARQL_SUMMARY_HTML_REPORT_TEMPLATE = "sparql_summary_report.jinja2"

QUERY_METADATA_TITLE = "title"
QUERY_METADATA_DESCRIPTION = "description"
QUERY_METADATA_XPATH = "xpath"
DEFAULT_QUERY_TITLE = "untitled query"
DEFAULT_QUERY_DESCRIPTION = "un-described query"
DEFAULT_QUERY_XPATH = []


class SPARQLTestSuiteRunner:
    """
        One of the assumptions is that all the SPARQL queries are of type ASK.
    """

    def __init__(self, rdf_manifestation: RDFManifestation, sparql_test_suite: SPARQLTestSuite,
                 mapping_suite: MappingSuite, xml_manifestation: XMLManifestation = None):
        self.rdf_manifestation = rdf_manifestation
        self.xml_manifestation = xml_manifestation
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
        xpath = metadata[QUERY_METADATA_XPATH].split(
            SPARQL_XPATH_SEPARATOR
        ) if QUERY_METADATA_XPATH in metadata and metadata[QUERY_METADATA_XPATH] else DEFAULT_QUERY_XPATH
        query = cls._sanitize_query(file_resource.file_content)
        return SPARQLQuery(title=title, description=description, xpath=xpath, query=query)

    def _process_sparql_ask_result(self, query_result, sparql_query: SPARQLQuery,
                                   sparql_query_result: SPARQLQueryResult):
        ask_answer = query_result.askAnswer
        sparql_query_result.query_result = str(ask_answer)

        # Initial result
        result: SPARQLQueryRefinedResultType = \
            SPARQLQueryRefinedResultType.VALID.value if ask_answer else SPARQLQueryRefinedResultType.INVALID.value

        xpath_coverage_validation = None
        if self.xml_manifestation:
            xpath_coverage_validation = self.xml_manifestation.xpath_coverage_validation
        if xpath_coverage_validation and xpath_coverage_validation.validation_result:
            xpath_validation_result = xpath_coverage_validation.validation_result

            sparql_query_result.fields_covered = any(
                map(lambda v: v in xpath_validation_result.xpath_covered, sparql_query.xpath))

            sparql_query_xpath = set(sparql_query.xpath)
            xpaths_in_notice = sparql_query_xpath & set(xpath_validation_result.xpath_covered)
            if len(xpaths_in_notice) < len(sparql_query_xpath):
                sparql_query_result.missing_fields = list(sparql_query_xpath - xpaths_in_notice)

            # Refined result
            if ask_answer and sparql_query_result.fields_covered:
                result = SPARQLQueryRefinedResultType.VALID.value
            elif not ask_answer and not sparql_query_result.fields_covered:
                result = SPARQLQueryRefinedResultType.UNVERIFIABLE.value
            elif ask_answer and not sparql_query_result.fields_covered:
                result = SPARQLQueryRefinedResultType.WARNING.value
            elif not ask_answer and sparql_query_result.fields_covered:
                result = SPARQLQueryRefinedResultType.INVALID.value

        sparql_query_result.result = result

    def execute_test_suite(self) -> SPARQLTestSuiteValidationReport:
        """
            Executing SPARQL queries from a SPARQL test suite and return execution details
        :return:
        """
        sparql_runner = SPARQLRunner(self.rdf_manifestation.object_data)
        test_suite_executions = SPARQLTestSuiteValidationReport(
            mapping_suite_identifier=self.mapping_suite.get_mongodb_id(),
            test_suite_identifier=self.sparql_test_suite.identifier,
            validation_results=[],
            object_data="SPARQLTestSuiteExecution")
        for query_file_resource in self.sparql_test_suite.sparql_tests:
            sparql_query: SPARQLQuery = self._sparql_query_from_file_resource(file_resource=query_file_resource)
            sparql_query_result = SPARQLQueryResult(query=sparql_query)
            try:
                sparql_query_result.identifier = Path(query_file_resource.file_name).stem
                query_result = sparql_runner.query(sparql_query.query)
                if query_result.type == "ASK":
                    self._process_sparql_ask_result(query_result, sparql_query, sparql_query_result)
                else:
                    sparql_query_result.query_result = query_result.serialize(format="json")
            except Exception as e:
                sparql_query_result.error = str(e)[:100]
                sparql_query_result.result = SPARQLQueryRefinedResultType.ERROR.value
            test_suite_executions.validation_results.append(sparql_query_result)

        test_suite_executions.validation_results.sort(key=lambda x: x.query.title)
        return test_suite_executions


class SPARQLReportBuilder:
    """
        Given a SPARQLQueryResult, generates JSON and HTML reports.
    """

    def __init__(self, sparql_test_suite_execution: SPARQLTestSuiteValidationReport, notice_ids: List[str] = None,
                 with_html: bool = False):
        """
        :param sparql_test_suite_execution:
        :param notice_ids:
        :param with_html: generate HTML report
        """
        self.sparql_test_suite_execution = sparql_test_suite_execution
        self.notice_ids = notice_ids
        self.with_html = with_html

    def generate_report(self) -> SPARQLTestSuiteValidationReport:
        if self.with_html:
            template_data: dict = self.sparql_test_suite_execution.dict()
            template_data[NOTICE_IDS_FIELD] = self.notice_ids
            html_report = TEMPLATES.get_template(SPARQL_TEST_SUITE_EXECUTION_HTML_REPORT_TEMPLATE).render(template_data)
            self.sparql_test_suite_execution.object_data = html_report
        return self.sparql_test_suite_execution


def generate_sparql_validation_summary_report(report_notices: List[ReportNotice], mapping_suite_package: MappingSuite,
                                              execute_full_validation: bool = True,
                                              with_html: bool = False,
                                              report: SPARQLValidationSummaryReport = None,
                                              metadata: dict = None) -> SPARQLValidationSummaryReport:
    if report is None:
        report: SPARQLValidationSummaryReport = SPARQLValidationSummaryReport(
            object_data="SPARQLValidationSummaryReport",
            notices=[],
            validation_results=[]
        )

    report.notices = sorted(NoticeTransformer.transform_validation_report_notices(report_notices, group_depth=1) + (
            report.notices or []), key=lambda report_data: report_data.notice_id)

    for report_notice in report_notices:
        notice = report_notice.notice
        validate_notice_with_sparql_suite(
            notice=notice,
            mapping_suite_package=mapping_suite_package,
            execute_full_validation=execute_full_validation,
            with_html=False
        )
        for sparql_validation in notice.rdf_manifestation.sparql_validations:
            test_suite_id = sparql_validation.test_suite_identifier
            report.test_suite_ids.append(test_suite_id)
            mapping_suite_versioned_id = sparql_validation.mapping_suite_identifier
            report.mapping_suite_ids.append(mapping_suite_versioned_id)

            validation: SPARQLQueryResult
            for validation in sparql_validation.validation_results:
                validation_query_result: SPARQLValidationSummaryQueryResult
                found_validation_query_result = list(filter(
                    lambda record:
                    (record.query.query == validation.query.query)
                    and (record.query.title == validation.query.title)
                    and (record.test_suite_identifier == test_suite_id),
                    report.validation_results
                ))

                if found_validation_query_result:
                    validation_query_result = found_validation_query_result[0]
                else:
                    validation_query_result = SPARQLValidationSummaryQueryResult(
                        test_suite_identifier=test_suite_id,
                        **validation.dict()
                    )

                notice_data: ReportPackageNoticeData = ReportPackageNoticeData(
                    notice_id=notice.ted_id,
                    path=str(report_notice.metadata.path),
                    mapping_suite_versioned_id=mapping_suite_versioned_id,
                    mapping_suite_identifier=mapping_suite_package.identifier
                )

                if validation.result == SPARQLQueryRefinedResultType.VALID.value:
                    validation_query_result.aggregate.valid.count += 1
                    validation_query_result.aggregate.valid.notices.append(notice_data)
                elif validation.result == SPARQLQueryRefinedResultType.UNVERIFIABLE.value:
                    validation_query_result.aggregate.unverifiable.count += 1
                    validation_query_result.aggregate.unverifiable.notices.append(notice_data)
                elif validation.result == SPARQLQueryRefinedResultType.INVALID.value:
                    validation_query_result.aggregate.invalid.count += 1
                    validation_query_result.aggregate.invalid.notices.append(notice_data)
                elif validation.result == SPARQLQueryRefinedResultType.WARNING.value:
                    validation_query_result.aggregate.warning.count += 1
                    validation_query_result.aggregate.warning.notices.append(notice_data)
                elif validation.result == SPARQLQueryRefinedResultType.ERROR.value:
                    validation_query_result.aggregate.error.count += 1
                    validation_query_result.aggregate.error.notices.append(notice_data)
                elif validation.result == SPARQLQueryRefinedResultType.UNKNOWN.value:
                    validation_query_result.aggregate.unknown.count += 1
                    validation_query_result.aggregate.unknown.notices.append(notice_data)

                if not found_validation_query_result:
                    report.validation_results.append(validation_query_result)

    report.test_suite_ids = list(set(report.test_suite_ids))
    report.mapping_suite_ids = list(set(report.mapping_suite_ids))

    if with_html:
        template_data: dict = report.dict()
        template_data[TEMPLATE_METADATA_KEY] = metadata
        html_report = TEMPLATES.get_template(SPARQL_SUMMARY_HTML_REPORT_TEMPLATE).render(template_data)
        report.object_data = html_report

    return report


def validate_notice_with_sparql_suite(notice: Notice, mapping_suite_package: MappingSuite,
                                      execute_full_validation: bool = True, with_html: bool = False) -> Notice:
    """
    Validates a notice with a sparql test suites
    :param with_html: generate HTML report
    :param notice:
    :param mapping_suite_package:
    :param execute_full_validation:
    :return:
    """

    def sparql_validation(notice_item: Notice, rdf_manifestation: RDFManifestation, with_html: bool = False) \
            -> List[SPARQLTestSuiteValidationReport]:
        reports = []
        sparql_test_suites = mapping_suite_package.sparql_test_suites
        for sparql_test_suite in sparql_test_suites:
            test_suite_execution = SPARQLTestSuiteRunner(rdf_manifestation=rdf_manifestation,
                                                         xml_manifestation=notice_item.xml_manifestation,
                                                         sparql_test_suite=sparql_test_suite,
                                                         mapping_suite=mapping_suite_package
                                                         ).execute_test_suite()
            report_builder = SPARQLReportBuilder(sparql_test_suite_execution=test_suite_execution,
                                                 notice_ids=[notice_item.ted_id], with_html=with_html)
            reports.append(report_builder.generate_report())
        return sorted(reports, key=lambda x: x.test_suite_identifier)

    if execute_full_validation:
        for report in sparql_validation(notice_item=notice, rdf_manifestation=notice.rdf_manifestation,
                                        with_html=with_html):
            notice.set_rdf_validation(rdf_validation=report)

    for report in sparql_validation(notice_item=notice, rdf_manifestation=notice.distilled_rdf_manifestation,
                                    with_html=with_html):
        notice.set_distilled_rdf_validation(rdf_validation=report)

    return notice


def validate_notice_by_id_with_sparql_suite(notice_id: str, mapping_suite_identifier: str,
                                            notice_repository: NoticeRepositoryABC,
                                            mapping_suite_repository: MappingSuiteRepositoryABC,
                                            with_html: bool = False):
    """
    Validates a notice by id with a sparql test suites
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
    validate_notice_with_sparql_suite(notice=notice, mapping_suite_package=mapping_suite_package, with_html=with_html)
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
