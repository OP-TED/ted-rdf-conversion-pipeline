import json
import pathlib
from typing import Optional

from src.ted_sws.data_manager.adapters.mapping_suite_repository import MS_METADATA_FILE_NAME, \
    MS_STANDARD_METADATA_VERSION_KEY, MS_METADATA_IDENTIFIER_KEY, \
    MS_EFORMS_METADATA_VERSION_KEY
from src.ted_sws.mapping_suite_processor.adapters.mapping_suite_structure_checker import MappingPackageStructureValidator


def get_mapping_package_id_from_file_system(mapping_package_path: pathlib.Path) -> Optional[str]:
    """
        This function return mapping_package_id from file system location.
    :param mapping_package_path:
    :return:
    """
    mapping_package_metadata_path = mapping_package_path / MS_METADATA_FILE_NAME

    if mapping_package_metadata_path.exists() and mapping_package_metadata_path.is_file():
        mapping_package_metadata = json.loads(mapping_package_metadata_path.read_text(encoding="utf-8"))
        identifier_value = mapping_package_metadata[MS_METADATA_IDENTIFIER_KEY]
        version_value = mapping_package_metadata[
            MS_STANDARD_METADATA_VERSION_KEY] if MS_STANDARD_METADATA_VERSION_KEY in mapping_package_metadata else \
        mapping_package_metadata[MS_EFORMS_METADATA_VERSION_KEY]
        return f"{identifier_value}_v{version_value}"
    return None


def validate_mapping_package(mapping_package_path: pathlib.Path) -> bool:
    """
        This function validate mapping package structure in file system.
    :param mapping_package_path:
    :return:
    """
    mapping_package_validator = MappingPackageStructureValidator(mapping_package_path)

    return mapping_package_validator.is_valid()
