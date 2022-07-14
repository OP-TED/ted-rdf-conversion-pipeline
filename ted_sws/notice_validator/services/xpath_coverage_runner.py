from datetime import datetime
from pathlib import Path
from typing import List, Union, Set, Dict

import numpy as np
import pandas as pd
from jinja2 import Environment, PackageLoader
from pymongo import MongoClient

from ted_sws.core.model.notice import Notice
from ted_sws.data_sampler.services.notice_xml_indexer import index_notice, get_unique_xpaths_covered_by_notices
from ted_sws.mapping_suite_processor import CONCEPTUAL_MAPPINGS_METADATA_SHEET_NAME
from ted_sws.mapping_suite_processor.services.conceptual_mapping_generate_sparql_queries import \
    CONCEPTUAL_MAPPINGS_RULES_SHEET_NAME, RULES_FIELD_XPATH, RULES_E_FORM_BT_NAME
from ted_sws.notice_validator import BASE_XPATH_FIELD
from ted_sws.notice_validator.model.coverage_report import XPATHCoverageReport, XPathCoverageAssertion

TEMPLATES = Environment(loader=PackageLoader("ted_sws.notice_validator.resources", "templates"))
XPATH_COVERAGE_REPORT_TEMPLATE = "xpath_coverage_report.jinja2"

PATH_TYPE = Union[str, Path]
XPATH_TYPE = Dict[str, List[str]]


class CoverageRunner:
    """
        Runs coverage measurement of the XML notice
    """

    conceptual_xpaths: Set[str]
    conceptual_xpath_names: Dict[str, str]
    mongodb_client: MongoClient
    base_xpath: str

    def __init__(self, conceptual_mappings_file_path: PATH_TYPE, xslt_transformer=None,
                 mongodb_client: MongoClient = None):
        with open(Path(conceptual_mappings_file_path), 'rb') as excel_file:
            metadata_df = pd.read_excel(excel_file, sheet_name=CONCEPTUAL_MAPPINGS_METADATA_SHEET_NAME)
            metadata = metadata_df.set_index('Field').T.to_dict('list')
            self.base_xpath = metadata[BASE_XPATH_FIELD][0]
            rules_df = pd.read_excel(excel_file, sheet_name=CONCEPTUAL_MAPPINGS_RULES_SHEET_NAME, header=1)
            df_xpaths = rules_df[RULES_FIELD_XPATH].tolist()
            df_bt_names = rules_df[RULES_E_FORM_BT_NAME].tolist()
            xpaths = []
            xpath_names = {}
            for idx, xpath_row in enumerate(df_xpaths):
                if xpath_row is not np.nan:
                    for xpath in xpath_row.split('\n'):
                        if xpath:
                            full_xpath = self.base_xpath + "/" + xpath
                            xpath_names[full_xpath] = df_bt_names[idx]
                            xpaths.append(full_xpath)
            self.conceptual_xpaths = set(xpaths)
            self.conceptual_xpath_names = xpath_names

        self.mongodb_client = mongodb_client
        self.xslt_transformer = xslt_transformer

    @classmethod
    def find_notice_by_xpath(cls, notice_xpaths: XPATH_TYPE, xpath: str) -> Dict[str, int]:
        notice_hit: Dict[str, int] = {k: v.count(xpath) for k, v in sorted(notice_xpaths.items()) if xpath in v}
        return notice_hit

    def xpath_assertions(self, notice_xpaths: XPATH_TYPE, xpaths_list: List[str]) -> List[XPathCoverageAssertion]:
        xpath_assertions = []
        for xpath in self.conceptual_xpaths:
            xpath_assertion = XPathCoverageAssertion()
            title = self.conceptual_xpath_names[xpath]
            xpath_assertion.title = title if title is not np.nan else ''
            xpath_assertion.xpath = xpath
            xpath_assertion.count = xpaths_list.count(xpath)
            xpath_assertion.notice_hit = self.find_notice_by_xpath(notice_xpaths, xpath)
            xpath_assertion.query_result = xpath_assertion.count > 0
            xpath_assertions.append(xpath_assertion)
        return xpath_assertions

    def xpath_coverage(self, report: XPATHCoverageReport, notice_xpaths: XPATH_TYPE, xpaths_list: List[str]):
        unique_notice_xpaths: Set[str] = set(xpaths_list)

        report.xpath_assertions = self.xpath_assertions(notice_xpaths, xpaths_list)
        report.xpath_covered = list(self.conceptual_xpaths & unique_notice_xpaths)
        report.xpath_not_covered = list(unique_notice_xpaths - self.conceptual_xpaths)
        report.xpath_extra = list(self.conceptual_xpaths - unique_notice_xpaths)
        if len(unique_notice_xpaths):
            report.coverage = len(report.xpath_covered) / len(unique_notice_xpaths)

    @classmethod
    def based_xpaths(cls, xpaths: List[str], base_xpath: str) -> List[str]:
        """

        :param xpaths:
        :param base_xpath:
        :return:
        """
        base_xpath += "/"
        return list(filter(lambda xpath: xpath.startswith(base_xpath), xpaths))

    def coverage_notice_xpath(self, notices: List[Notice], mapping_suite_id) -> XPATHCoverageReport:
        report: XPATHCoverageReport = XPATHCoverageReport()
        report.created_at = datetime.now().isoformat()
        report.mapping_suite_id = mapping_suite_id
        notice_id = []

        notice_xpaths: XPATH_TYPE = {}
        xpaths_list: List[str] = []
        for notice in notices:
            xpaths: List[str] = []
            notice_id.append(notice.ted_id)
            if self.mongodb_client is not None:
                xpaths = get_unique_xpaths_covered_by_notices([notice.ted_id], self.mongodb_client)
            else:
                notice = index_notice(notice, self.xslt_transformer, False)

                if notice.xml_metadata and notice.xml_metadata.xpaths:
                    xpaths = notice.xml_metadata.xpaths

            notice_xpaths[notice.ted_id] = self.based_xpaths(xpaths, self.base_xpath)
            xpaths_list += notice_xpaths[notice.ted_id]

        report.notice_id = sorted(notice_id)
        self.xpath_coverage(report, notice_xpaths, xpaths_list)

        return report

    @classmethod
    def json_report(cls, report: XPATHCoverageReport) -> dict:
        return report.dict()

    @classmethod
    def html_report(cls, report: XPATHCoverageReport) -> str:
        data: dict = cls.json_report(report)
        html_report = TEMPLATES.get_template(XPATH_COVERAGE_REPORT_TEMPLATE).render(data)
        return html_report


def coverage_notice_xpath_report(notices: List[Notice], mapping_suite_id,
                                 conceptual_mappings_file_path: PATH_TYPE = None,
                                 coverage_runner: CoverageRunner = None, xslt_transformer=None,
                                 mongodb_client: MongoClient = None) -> XPATHCoverageReport:
    if not coverage_runner:
        coverage_runner = CoverageRunner(conceptual_mappings_file_path, xslt_transformer, mongodb_client)
    report = coverage_runner.coverage_notice_xpath(notices, mapping_suite_id)
    return report
