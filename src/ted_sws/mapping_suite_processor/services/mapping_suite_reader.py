from pathlib import Path
from typing import Dict

from src.ted_sws.core.model.transform import MappingPackageType
from src.ted_sws.mapping_suite_processor.adapters.mapping_suite_reader import MappingPackageReader

STANDARD_FORM_VERSION_KEY = "version"
EFORM_VERSION_KEY = "mapping_version"
MAPPING_TYPE_KEY = "mapping_type"
MAPPING_PACKAGE_HASH = "mapping_suite_hash_digest"


def mapping_package_read_metadata(mapping_package_path: Path) -> Dict:
    return MappingPackageReader.mapping_package_read_metadata(mapping_package_path)
