from pathlib import Path
from typing import Dict

from ted_sws.mapping_suite_processor.adapters.mapping_suite_reader import MappingSuiteReader

VERSION_KEY = "version"
MAPPING_SUITE_HASH = "mapping_suite_hash_digest"


def mapping_suite_read_metadata(mapping_suite_path: Path) -> Dict:
    return MappingSuiteReader.mapping_suite_read_metadata(mapping_suite_path)
