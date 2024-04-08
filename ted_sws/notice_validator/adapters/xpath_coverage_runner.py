import io
import xml.etree.ElementTree as ET
from typing import List, Set, Dict

from jinja2 import Environment, PackageLoader
from saxonche import PySaxonProcessor, PySaxonApiError

from ted_sws.core.model.manifestation import XPATHCoverageValidationReport, XPATHCoverageValidationAssertion, \
    XPATHCoverageValidationResult
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.transform import MappingXPATH, MappingSuite
from ted_sws.core.model.validation_report import ReportNotice
from ted_sws.data_sampler.services.notice_xml_indexer import index_notice
from ted_sws.mapping_suite_processor.adapters.mapping_suite_reader import MappingSuiteReader
from ted_sws.notice_transformer.services.notice_transformer import transform_report_notices
from ted_sws.notice_validator.resources.templates import TEMPLATE_METADATA_KEY

TEMPLATES = Environment(loader=PackageLoader("ted_sws.notice_validator.resources", "templates"))
XPATH_COVERAGE_REPORT_TEMPLATE = "xpath_coverage_report.jinja2"

XPathDict = Dict[str, List[str]]


class CoverageRunner:
    """"""
    mapping_suite: MappingSuite
    mapping_suite_id: str
    conceptual_xpaths: Set[str] = set()
    conceptual_xpath_data: Dict[str, MappingXPATH] = {}

    def __init__(self, mapping_suite: MappingSuite):
        """"""
        self.mapping_suite = mapping_suite
        self.mapping_suite_id = mapping_suite.get_mongodb_id()
        self.init_xpath_data(mapping_suite=mapping_suite)

    @classmethod
    def notice_xpaths(cls, notice: Notice) -> List[str]:
        if not notice.xml_metadata or not notice.xml_metadata.unique_xpaths:
            notice = index_notice(notice)
        return notice.xml_metadata.unique_xpaths

    def init_xpath_data(self, mapping_suite: MappingSuite):
        for cm_xpath in MappingSuiteReader.read_mapping_suite_xpaths(mapping_suite):
            self.conceptual_xpaths.add(cm_xpath.xpath)
            self.conceptual_xpath_data[cm_xpath.xpath] = cm_xpath

    def xpath_coverage_validation_report(self, notice: Notice) -> XPATHCoverageValidationReport:
        report: XPATHCoverageValidationReport = XPATHCoverageValidationReport(
            object_data="XPATHCoverageValidationReport",
            mapping_suite_identifier=self.mapping_suite_id)

        xpaths: List[str] = []
        for xpath in self.get_all_conceptual_xpaths():
            if self.check_xpath_expression_with_xml(notice.xml_manifestation.object_data, xpath):
                xpaths.append(xpath)
        notice_xpaths: XPathDict = {notice.ted_id: xpaths}
        self.validate_xpath_coverage_report(report, notice_xpaths, xpaths)

        return report

    @classmethod
    def find_notice_by_xpath(cls, notice_xpaths: XPathDict, xpath: str) -> Dict[str, int]:
        notice_hit: Dict[str, int] = {k: v.count(xpath) for k, v in sorted(notice_xpaths.items()) if xpath in v}
        return notice_hit

    def get_all_conceptual_xpaths(self) -> Set[str]:
        return self.conceptual_xpaths

    @classmethod
    def extract_namespaces(cls, xml_content):
        xml_file = io.StringIO(xml_content)
        namespaces = dict()
        for event, elem in ET.iterparse(xml_file, events=('start-ns',)):
            ns, url = elem
            namespaces[ns] = url
        return namespaces

    @classmethod
    def check_xpath_expression_with_xml(cls, xml_content, xpath_expression) -> bool:
        namespaces = cls.extract_namespaces(xml_content)
        with PySaxonProcessor(license=False) as proc:
            xp = proc.new_xpath_processor()
            for prefix, ns_uri in namespaces.items():
                xp.declare_namespace(prefix, ns_uri)
            document = proc.parse_xml(xml_text=xml_content)
            xp.set_context(xdm_item=document)
            try:
                item = xp.evaluate_single(xpath_expression)
                return True if item else False
            except PySaxonApiError:
                return False

    def xpath_assertions(
            self, notice_xpaths: XPathDict, xpaths_list: List[str]
    ) -> List[XPATHCoverageValidationAssertion]:
        xpath_assertions = []
        for xpath in self.get_all_conceptual_xpaths():
            xpath_assertion = XPATHCoverageValidationAssertion()
            xpath_data = self.conceptual_xpath_data[xpath]
            form_field = xpath_data.form_field
            xpath_assertion.form_field = form_field if form_field else ''
            xpath_assertion.xpath = xpath
            xpath_assertion.count = xpaths_list.count(xpath)
            xpath_assertion.notice_hit = self.find_notice_by_xpath(notice_xpaths, xpath)
            xpath_assertion.query_result = xpath_assertion.count > 0
            xpath_assertions.append(xpath_assertion)
        return sorted(xpath_assertions, key=lambda x: x.form_field)

    def validate_xpath_coverage_report(
            self, report: XPATHCoverageValidationReport, notice_xpaths: XPathDict, xpaths_list: List[str]
    ):
        unique_notice_xpaths: Set[str] = set(xpaths_list)

        validation_result: XPATHCoverageValidationResult = XPATHCoverageValidationResult()
        validation_result.xpath_assertions = self.xpath_assertions(notice_xpaths, xpaths_list)
        validation_result.xpath_covered = sorted(list(self.conceptual_xpaths & unique_notice_xpaths))

        report.validation_result = validation_result

    def xpath_coverage_validation_summary_report(
            self, notices: List[ReportNotice]
    ) -> XPATHCoverageValidationReport:
        report: XPATHCoverageValidationReport = XPATHCoverageValidationReport(
            object_data="XPATHCoverageValidationReport",
            mapping_suite_identifier=self.mapping_suite_id)

        notice_xpaths: XPathDict = {}
        xpaths_list: List[str] = []
        for report_notice in notices:
            notice = report_notice.notice
            xpaths: List[str] = []
            for xpath in self.get_all_conceptual_xpaths():
                if self.check_xpath_expression_with_xml(
                        report_notice.notice.xml_manifestation.object_data, xpath
                ):
                    xpaths.append(xpath)

            notice_xpaths[notice.ted_id] = xpaths
            xpaths_list += notice_xpaths[notice.ted_id]

        self.validate_xpath_coverage_report(report, notice_xpaths, xpaths_list)
        report.validation_result.notices = sorted(transform_report_notices(notices),
                                                  key=lambda report_data: report_data.notice_id)

        return report

    @classmethod
    def json_report(cls, report: XPATHCoverageValidationReport) -> dict:
        return report.dict()

    @classmethod
    def html_report(cls, report: XPATHCoverageValidationReport, metadata: dict = None) -> str:
        data: dict = cls.json_report(report)
        data[TEMPLATE_METADATA_KEY] = metadata
        html_report = TEMPLATES.get_template(XPATH_COVERAGE_REPORT_TEMPLATE).render(data)
        return html_report
