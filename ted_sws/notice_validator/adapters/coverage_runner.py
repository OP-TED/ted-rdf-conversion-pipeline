import xml.etree.ElementTree as ET

from ted_sws.notice_validator.model.coverage_report import NoticeCoverageReport
from ted_sws.mapping_suite_processor.services.conceptual_mapping_generate_sparql_queries import \
    CONCEPTUAL_MAPPINGS_RULES_SHEET_NAME, RULES_FIELD_XPATH
from ted_sws.mapping_suite_processor.services.conceptual_mapping_generate_metadata import \
    CONCEPTUAL_MAPPINGS_METADATA_SHEET_NAME
from typing import List, Union
from pathlib import Path
import pandas as pd

PATH_TYPE = Union[str, Path]


class CoverageRunner:
    """
        Runs coverage measurement of the XML notice
    """

    conceptual_mappings_file_path: Path

    def __init__(self, conceptual_mappings_file_path: PATH_TYPE):
        with open(Path(conceptual_mappings_file_path), 'r') as excel_file:
            metadata_df = pd.read_excel(excel_file, sheet_name=CONCEPTUAL_MAPPINGS_METADATA_SHEET_NAME)
            metadata = metadata_df.set_index('Field').T.to_dict('list')
            rules_df = pd.read_excel(excel_file, sheet_name=CONCEPTUAL_MAPPINGS_RULES_SHEET_NAME)
            rules = metadata_df.set_index(RULES_FIELD_XPATH).T.to_dict('list')
            print("METADATA :: ", metadata)
            print("RULES :: ", rules)

    def coverage_notice(self, notice_content) -> NoticeCoverageReport:
        report: NoticeCoverageReport = None
        return report

    def coverage_files(self, files: [PATH_TYPE]) -> List[NoticeCoverageReport]:
        """
        """
        reports: List[NoticeCoverageReport] = []
        for file in files:
            path = Path(file)
            with open(path, 'r') as f:
                cov_report: NoticeCoverageReport = self.coverage_notice(f.read())
        return reports
