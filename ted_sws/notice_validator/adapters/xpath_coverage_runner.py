from pathlib import Path
from typing import List, Union, Set, Dict

import numpy as np
from jinja2 import Environment, PackageLoader
from pymongo import MongoClient

from ted_sws.core.model.manifestation import XPATHCoverageValidationReport, XPATHCoverageValidationAssertion, \
    XPATHCoverageValidationResult, NoticeForReport
from ted_sws.core.model.transform import ConceptualMapping, ConceptualMappingXPATH
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryMongoDB
from ted_sws.data_sampler.services.notice_xml_indexer import index_notice, get_unique_xpaths_covered_by_notices
from ted_sws.mapping_suite_processor.services.conceptual_mapping_reader import mapping_suite_read_conceptual_mapping

TEMPLATES = Environment(loader=PackageLoader("ted_sws.notice_validator.resources", "templates"))
XPATH_COVERAGE_REPORT_TEMPLATE = "xpath_coverage_report.jinja2"

PATH_TYPE = Union[str, Path]
XPATH_TYPE = Dict[str, List[str]]


class CoverageRunner:
    """
        Runs coverage measurement of the XML notice
    """

    conceptual_xpaths: Set[str] = set()
    conceptual_xpath_data: Dict[str, ConceptualMappingXPATH] = {}
    mongodb_client: MongoClient
    base_xpath: str
    mapping_suite_id: str

    def __init__(self, mapping_suite_id: str, conceptual_mappings_file_path: PATH_TYPE = None,
                 mongodb_client: MongoClient = None):
        self.mapping_suite_id = mapping_suite_id
        self.mongodb_client = mongodb_client

        conceptual_mapping: ConceptualMapping
        if self._db_readable():
            mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
            mapping_suite = mapping_suite_repository.get(reference=mapping_suite_id)
            if mapping_suite is None:
                raise ValueError(f'Mapping suite, with {mapping_suite_id} id, was not found')
            conceptual_mapping: ConceptualMapping = mapping_suite.conceptual_mapping
        else:
            conceptual_mapping = mapping_suite_read_conceptual_mapping(Path(conceptual_mappings_file_path))

        for cm_xpath in conceptual_mapping.xpaths:
            self.conceptual_xpaths.add(cm_xpath.xpath)
            self.conceptual_xpath_data[cm_xpath.xpath] = cm_xpath

        self.base_xpath = conceptual_mapping.metadata.base_xpath

    def _db_readable(self) -> bool:
        return self.mongodb_client is not None

    @classmethod
    def find_notice_by_xpath(cls, notice_xpaths: XPATH_TYPE, xpath: str) -> Dict[str, int]:
        notice_hit: Dict[str, int] = {k: v.count(xpath) for k, v in sorted(notice_xpaths.items()) if xpath in v}
        return notice_hit

    def xpath_assertions(self, notice_xpaths: XPATH_TYPE,
                         xpaths_list: List[str]) -> List[XPATHCoverageValidationAssertion]:
        xpath_assertions = []
        for xpath in self.conceptual_xpaths:
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

    def validate_xpath_coverage_report(self, report: XPATHCoverageValidationReport, notice_xpaths: XPATH_TYPE,
                                       xpaths_list: List[str], notices: List[NoticeForReport]):
        unique_notice_xpaths: Set[str] = set(xpaths_list)

        validation_result: XPATHCoverageValidationResult = XPATHCoverageValidationResult()
        validation_result.notices = sorted(notices, key=lambda notice: notice.ted_id)
        validation_result.xpath_assertions = self.xpath_assertions(notice_xpaths, xpaths_list)
        validation_result.xpath_covered = sorted(list(self.conceptual_xpaths & unique_notice_xpaths))
        validation_result.xpath_not_covered = sorted(list(unique_notice_xpaths - self.conceptual_xpaths))
        validation_result.xpath_extra = sorted(list(self.conceptual_xpaths - unique_notice_xpaths))
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
        base_xpath += "/"
        return list(filter(lambda xpath: xpath.startswith(base_xpath), xpaths))

    def coverage_notice_xpath(self, notices: List[NoticeForReport], mapping_suite_id) -> XPATHCoverageValidationReport:
        report: XPATHCoverageValidationReport = XPATHCoverageValidationReport(
            object_data="XPATHCoverageValidationReport",
            mapping_suite_identifier=mapping_suite_id)

        notice_xpaths: XPATH_TYPE = {}
        xpaths_list: List[str] = []
        for notice_for_report in notices:
            notice = notice_for_report.notice
            xpaths: List[str] = []
            if self._db_readable():
                xpaths = get_unique_xpaths_covered_by_notices([notice.ted_id], self.mongodb_client)
            else:
                notice = index_notice(notice)

                if notice.xml_metadata and notice.xml_metadata.unique_xpaths:
                    xpaths = notice.xml_metadata.unique_xpaths

            notice_xpaths[notice.ted_id] = self.based_xpaths(xpaths, self.base_xpath)
            xpaths_list += notice_xpaths[notice.ted_id]

        self.validate_xpath_coverage_report(report, notice_xpaths, xpaths_list, notices)

        return report

    @classmethod
    def json_report(cls, report: XPATHCoverageValidationReport) -> dict:
        return report.dict()

    @classmethod
    def html_report(cls, report: XPATHCoverageValidationReport) -> str:
        data: dict = cls.json_report(report)
        html_report = TEMPLATES.get_template(XPATH_COVERAGE_REPORT_TEMPLATE).render(data)
        return html_report
