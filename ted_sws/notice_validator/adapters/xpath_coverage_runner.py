from typing import List, Set, Dict

import numpy as np
from jinja2 import Environment, PackageLoader

from ted_sws.core.model.manifestation import XPATHCoverageValidationReport, XPATHCoverageValidationAssertion, \
    XPATHCoverageValidationResult
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.transform import ConceptualMapping, ConceptualMappingXPATH, MappingSuite
from ted_sws.core.model.validation_report import ReportNotice
from ted_sws.data_sampler.services.notice_xml_indexer import index_notice
from ted_sws.mapping_suite_processor.adapters.conceptual_mapping_reader import ConceptualMappingReader
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
    conceptual_remarked_xpaths: Set[str] = set()
    conceptual_xpath_data: Dict[str, ConceptualMappingXPATH] = {}
    base_xpath: str

    def __init__(self, mapping_suite: MappingSuite):
        """"""
        self.mapping_suite = mapping_suite
        self.mapping_suite_id = mapping_suite.get_mongodb_id()
        conceptual_mapping: ConceptualMapping = mapping_suite.conceptual_mapping
        self.init_xpath_data(conceptual_mapping=conceptual_mapping)

    @classmethod
    def notice_xpaths(cls, notice: Notice) -> List[str]:
        if not notice.xml_metadata or not notice.xml_metadata.unique_xpaths:
            notice = index_notice(notice)
        return notice.xml_metadata.unique_xpaths

    def init_xpath_data(self, conceptual_mapping: ConceptualMapping):
        for cm_xpath in conceptual_mapping.mapping_remarks:
            for xpath in cm_xpath.field_xpath:
                self.conceptual_remarked_xpaths.add(xpath)
                self.conceptual_xpath_data[xpath] = ConceptualMappingXPATH(
                    xpath=xpath,
                    form_field=f"{cm_xpath.standard_form_field_id} - {cm_xpath.standard_form_field_name}"
                )
        for cm_xpath in conceptual_mapping.xpaths:
            self.conceptual_xpaths.add(cm_xpath.xpath)
            self.conceptual_xpath_data[cm_xpath.xpath] = cm_xpath
        self.base_xpath = conceptual_mapping.metadata.base_xpath

    def xpath_coverage_validation_report(self, notice: Notice) -> XPATHCoverageValidationReport:
        report: XPATHCoverageValidationReport = XPATHCoverageValidationReport(
            object_data="XPATHCoverageValidationReport",
            mapping_suite_identifier=self.mapping_suite_id)

        xpaths: List[str] = self.notice_xpaths(notice=notice)
        based_xpaths = self.based_xpaths(xpaths, self.base_xpath)
        notice_xpaths: XPathDict = {notice.ted_id: based_xpaths}
        self.validate_xpath_coverage_report(report, notice_xpaths, based_xpaths)

        return report

    @classmethod
    def find_notice_by_xpath(cls, notice_xpaths: XPathDict, xpath: str) -> Dict[str, int]:
        notice_hit: Dict[str, int] = {k: v.count(xpath) for k, v in sorted(notice_xpaths.items()) if xpath in v}
        return notice_hit

    def get_all_conceptual_xpaths(self) -> Set[str]:
        return self.conceptual_remarked_xpaths | self.conceptual_xpaths

    def xpath_assertions(self, notice_xpaths: XPathDict,
                         xpaths_list: List[str]) -> List[XPATHCoverageValidationAssertion]:
        xpath_assertions = []
        for xpath in self.get_all_conceptual_xpaths():
            xpath_assertion = XPATHCoverageValidationAssertion()
            xpath_data = self.conceptual_xpath_data[xpath]
            form_field = xpath_data.form_field
            xpath_assertion.form_field = form_field if form_field is not np.nan else ''
            xpath_assertion.xpath = xpath
            xpath_assertion.count = xpaths_list.count(xpath)
            xpath_assertion.notice_hit = self.find_notice_by_xpath(notice_xpaths, xpath)
            xpath_assertion.query_result = xpath_assertion.count > 0
            xpath_assertions.append(xpath_assertion)
        return sorted(xpath_assertions, key=lambda x: x.form_field)

    def validate_xpath_coverage_report(self, report: XPATHCoverageValidationReport, notice_xpaths: XPathDict,
                                       xpaths_list: List[str]):
        unique_notice_xpaths: Set[str] = set(xpaths_list)

        validation_result: XPATHCoverageValidationResult = XPATHCoverageValidationResult()
        validation_result.xpath_assertions = self.xpath_assertions(notice_xpaths, xpaths_list)
        validation_result.xpath_covered = sorted(list(self.conceptual_xpaths & unique_notice_xpaths))
        all_conceptual_xpaths = self.get_all_conceptual_xpaths()
        validation_result.xpath_not_covered = sorted(list(unique_notice_xpaths - all_conceptual_xpaths))
        validation_result.xpath_extra = sorted(list(all_conceptual_xpaths - unique_notice_xpaths))
        validation_result.remarked_xpaths = sorted(list(self.conceptual_remarked_xpaths))
        unique_notice_xpaths_len = len(unique_notice_xpaths)
        xpath_covered_len = len(validation_result.xpath_covered)
        conceptual_xpaths_len = len(self.conceptual_xpaths)
        if unique_notice_xpaths_len:
            validation_result.coverage = xpath_covered_len / unique_notice_xpaths_len
        if conceptual_xpaths_len:
            validation_result.conceptual_coverage = xpath_covered_len / conceptual_xpaths_len

        report.validation_result = validation_result

    @classmethod
    def based_xpaths(cls, xpaths: List[str], base_xpath: str) -> List[str]:
        """
        :param xpaths:
        :param base_xpath:
        :return:
        """
        base_xpath = ConceptualMappingReader.base_xpath_as_prefix(base_xpath)
        return list(filter(lambda xpath: xpath.startswith(base_xpath), xpaths))

    def xpath_coverage_validation_summary_report(self,
                                                 notices: List[ReportNotice]
                                                 ) -> XPATHCoverageValidationReport:
        report: XPATHCoverageValidationReport = XPATHCoverageValidationReport(
            object_data="XPATHCoverageValidationReport",
            mapping_suite_identifier=self.mapping_suite_id)

        notice_xpaths: XPathDict = {}
        xpaths_list: List[str] = []
        for report_notice in notices:
            notice = report_notice.notice
            xpaths: List[str] = self.notice_xpaths(notice=notice)

            notice_xpaths[notice.ted_id] = self.based_xpaths(xpaths, self.base_xpath)
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
