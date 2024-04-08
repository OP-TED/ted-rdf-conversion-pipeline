import json
from pathlib import Path
from typing import Dict, List, Tuple

from ted_sws.core.model.transform import MappingXPATH, MappingSuite
from ted_sws.data_manager.adapters.mapping_suite_repository import MS_METADATA_FILE_NAME, MS_VALIDATE_FOLDER_NAME, \
    MS_SPARQL_FOLDER_NAME

# This set of constants refers to fields in the Conceptual Mapping file
VERSION_FIELD = 'Mapping Version'

CONCEPTUAL_MAPPINGS_ASSERTIONS = "cm_assertions"

SPARQL_QUERY_METADATA_TITLE = "title"
SPARQL_QUERY_METADATA_DESCRIPTION = "description"
SPARQL_QUERY_METADATA_XPATH = "xpath"


class MappingSuiteReader:
    """
    This adapter can be used to read different MappingSuite data
    """

    @classmethod
    def mapping_suite_read_metadata(cls, mapping_suite_path: Path) -> Dict:
        """
        This feature allows you to read the conceptual mapping metadata.
        :param mapping_suite_path:
        :return:
        """
        with open(mapping_suite_path / MS_METADATA_FILE_NAME) as metadata_file:
            metadata = json.load(metadata_file)

        return metadata

    @classmethod
    def extract_metadata_from_sparql_query(cls, content) -> dict:
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

    @classmethod
    def read_mapping_suite_xpaths(cls, mapping_suite: MappingSuite) -> List[MappingXPATH]:
        """

        :param mapping_suite:
        :return:
        """

        xpaths = []
        processed_xpaths = set()

        for test_suite in mapping_suite.sparql_test_suites:
            if test_suite != CONCEPTUAL_MAPPINGS_ASSERTIONS:
                continue

            for sparql_test in test_suite.sparql_tests:
                metadata = cls.extract_metadata_from_sparql_query(sparql_test.file_content)
                xpath = metadata[SPARQL_QUERY_METADATA_XPATH]
                if xpath not in processed_xpaths:
                    cm_xpath: MappingXPATH = MappingXPATH(
                        xpath=xpath,
                        form_field=metadata[SPARQL_QUERY_METADATA_TITLE]
                    )
                    xpaths.append(cm_xpath)
                    processed_xpaths.add(xpath)
            break

        return xpaths
