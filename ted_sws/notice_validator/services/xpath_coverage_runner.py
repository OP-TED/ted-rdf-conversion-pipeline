from datetime import datetime
from pathlib import Path
from typing import List, Union

import pandas as pd
from pymongo import MongoClient

from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.core.model.notice import Notice
from ted_sws.data_sampler.services.notice_xml_indexer import index_notice, get_unique_xpaths_covered_by_notices
from ted_sws.mapping_suite_processor import CONCEPTUAL_MAPPINGS_METADATA_SHEET_NAME
from ted_sws.mapping_suite_processor.services.conceptual_mapping_generate_sparql_queries import \
    CONCEPTUAL_MAPPINGS_RULES_SHEET_NAME, RULES_FIELD_XPATH
from ted_sws.notice_validator import BASE_XPATH_FIELD
from ted_sws.notice_validator.model.coverage_report import NoticeCoverageReport, XPathAssertion
from ted_sws import config

PATH_TYPE = Union[str, Path]


class CoverageRunner:
    """
        Runs coverage measurement of the XML notice
    """

    conceptual_xpaths: set
    base_xpath: str

    def __init__(self, conceptual_mappings_file_path: PATH_TYPE, xslt_transformer=None):
        with open(Path(conceptual_mappings_file_path), 'rb') as excel_file:
            metadata_df = pd.read_excel(excel_file, sheet_name=CONCEPTUAL_MAPPINGS_METADATA_SHEET_NAME)
            metadata = metadata_df.set_index('Field').T.to_dict('list')
            self.base_xpath = metadata[BASE_XPATH_FIELD][0]
            rules_df = pd.read_excel(excel_file, sheet_name=CONCEPTUAL_MAPPINGS_RULES_SHEET_NAME, header=1)
            df_xpaths = rules_df[RULES_FIELD_XPATH][pd.notnull(rules_df[RULES_FIELD_XPATH])].tolist()
            xpaths = []
            for xpath in df_xpaths:
                xpaths.extend(map(lambda x: (self.base_xpath + "/" + x), xpath.split('\n')))
            self.conceptual_xpaths = set(xpaths)

        self.xslt_transformer = xslt_transformer

    def xpath_assertions(self, notice_xpaths) -> List[XPathAssertion]:
        xpath_assertions = []
        for xpath in self.conceptual_xpaths:
            xpath_assertion = XPathAssertion()
            xpath_assertion.title = ""
            xpath_assertion.xpath = xpath
            xpath_assertion.count = notice_xpaths.count(xpath)
            xpath_assertion.query_result = xpath_assertion.count > 0
            xpath_assertion.required = True
            xpath_assertions.append(xpath_assertion)
        return xpath_assertions

    def xpath_desertions(self, notice_xpaths) -> List[str]:
        return list(set(notice_xpaths) - self.conceptual_xpaths)

    @classmethod
    def based_xpaths(cls, xpaths: List[str], base_xpath: str) -> List[str]:
        """

        :param xpaths:
        :param base_xpath:
        :return:
        """
        base_xpath += "/"
        return list(filter(lambda xpath: xpath.startswith(base_xpath), xpaths))

    def coverage_notice_xpath(self, notice_id, notice_content, mapping_suite_id,
                              mongodb_client: MongoClient = None) -> NoticeCoverageReport:
        report: NoticeCoverageReport = NoticeCoverageReport()
        report.created_at = datetime.now().isoformat()
        report.mapping_suite_id = mapping_suite_id
        report.notice_id = notice_id

        if mongodb_client is None and config.MONGO_DB_AUTH_URL is not None:
            mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)

        unique_xpaths: List[str] = []

        if mongodb_client is not None:
            unique_xpaths = get_unique_xpaths_covered_by_notices([notice_id], mongodb_client)

        if len(unique_xpaths) == 0:
            notice: Notice = Notice(notice_id=notice_id, xml_manifestation=XMLManifestation(object_data=notice_content))
            notice = index_notice(notice, self.xslt_transformer)
            unique_xpaths = notice.xml_metadata.unique_xpaths

        notice_xpaths = self.based_xpaths(unique_xpaths, self.base_xpath)
        report.xpath_assertions = self.xpath_assertions(notice_xpaths)
        report.xpath_desertions = self.xpath_desertions(notice_xpaths)
        report.coverage = self.xpath_desertions(notice_xpaths)

        return report

    @classmethod
    def json_report(cls, report: NoticeCoverageReport) -> dict:
        return report.dict()


def coverage_notice_xpath_report(notice_id, notice_content,
                                 mapping_suite_id, conceptual_mappings_file_path: PATH_TYPE = None,
                                 coverage_runner: CoverageRunner = None, xslt_transformer=None) -> dict:
    if not coverage_runner:
        coverage_runner = CoverageRunner(conceptual_mappings_file_path, xslt_transformer)
    report = coverage_runner.coverage_notice_xpath(notice_id, notice_content, mapping_suite_id)
    return coverage_runner.json_report(report)
