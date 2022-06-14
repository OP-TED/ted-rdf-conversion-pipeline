import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Union

import pandas as pd

from ted_sws.core.adapters.xml_preprocessor import XMLPreprocessor
from ted_sws.data_sampler.services.notice_xml_indexer import UNIQUE_XPATHS_XSLT_FILE_PATH, XSLT_PREFIX_RESULT
from ted_sws.mapping_suite_processor.services.conceptual_mapping_generate_metadata import \
    CONCEPTUAL_MAPPINGS_METADATA_SHEET_NAME
from ted_sws.mapping_suite_processor.services.conceptual_mapping_generate_sparql_queries import \
    CONCEPTUAL_MAPPINGS_RULES_SHEET_NAME, RULES_FIELD_XPATH
from ted_sws.notice_validator.model.coverage_report import NoticeCoverageReport, XPathAssertion
from ted_sws.resources import XSLT_FILES_PATH

PATH_TYPE = Union[str, Path]

BASE_XPATH_FIELD = "Base XPath"


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
        base_xpath += "/"
        return list(filter(lambda xpath: xpath.startswith(base_xpath), xpaths))

    def coverage_notice_xpath(self, notice_id, notice_content, mapping_suite_id) -> NoticeCoverageReport:
        report: NoticeCoverageReport = NoticeCoverageReport()
        report.created_at = datetime.now().isoformat()
        report.mapping_suite_id = mapping_suite_id
        report.notice_id = notice_id
        tmp = tempfile.NamedTemporaryFile()

        xml_path = tmp.name
        with open(xml_path, 'w') as f:
            f.write(notice_content)
            f.close()

        if self.xslt_transformer is None:
            xslt_transformer = XMLPreprocessor()
        else:
            xslt_transformer = self.xslt_transformer
        xslt_path = XSLT_FILES_PATH / UNIQUE_XPATHS_XSLT_FILE_PATH
        result = xslt_transformer.transform_with_xslt_to_string(xml_path=Path(xml_path),
                                                                xslt_path=xslt_path)
        notice_xpaths = self.based_xpaths(result[len(XSLT_PREFIX_RESULT):].split(","), self.base_xpath)
        report.xpath_assertions = self.xpath_assertions(notice_xpaths)
        report.xpath_desertions = self.xpath_desertions(notice_xpaths)

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
