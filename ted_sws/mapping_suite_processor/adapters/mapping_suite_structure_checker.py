import json
import pathlib
from typing import List

from ted_sws.core.model.transform import MetadataConstraints
from ted_sws.data_manager.adapters.mapping_suite_repository import MS_TRANSFORM_FOLDER_NAME, MS_TEST_DATA_FOLDER_NAME, \
    MS_CONCEPTUAL_MAPPING_FILE_NAME, MS_RESOURCES_FOLDER_NAME, MS_MAPPINGS_FOLDER_NAME, MS_METADATA_FILE_NAME, \
    MS_VALIDATE_FOLDER_NAME, MS_SPARQL_FOLDER_NAME, MS_SHACL_FOLDER_NAME, MS_OUTPUT_FOLDER_NAME, MS_TEST_SUITE_REPORT
from ted_sws.event_manager.adapters.event_handler_config import CLILoggerConfig
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.model.event_message import EventMessage
from ted_sws.event_manager.services.logger_from_context import get_env_logger
from ted_sws.data_manager.adapters.mapping_suite_repository import mapping_suite_read_conceptual_mapping
from ted_sws.mapping_suite_processor.services.conceptual_mapping_reader import mapping_suite_read_metadata

logger = get_env_logger(EventLogger(CLILoggerConfig()), is_cli=True)


def assert_path(assertion_path_list: List[pathlib.Path]) -> bool:
    """
        Validate whether the given path exists and is non empty.
    """
    is_valid = True
    for path_item in assertion_path_list:
        message_path_not_found = f"Path not found: {path_item}"
        if not path_item.exists():
            logger.error(event_message=EventMessage(message=message_path_not_found))
            is_valid = False

        if path_item.is_dir():
            message_folder_empty = f"Folder is empty: {path_item}"
            if not any(path_item.iterdir()):
                logger.error(event_message=EventMessage(message=message_folder_empty))
                is_valid = False
        else:
            message_file_is_empty = f"File is empty: {path_item}"
            if not path_item.stat().st_size > 0:
                logger.error(event_message=EventMessage(message=message_file_is_empty))
                is_valid = False

    return is_valid


def validate_mapping_suite_structure_lv1(package_folder_path_for_validator: pathlib.Path) -> bool:
    """
        Check whether the core mapping suite structure is in place.
    """
    mandatory_paths_l1 = [
        package_folder_path_for_validator / MS_TRANSFORM_FOLDER_NAME,
        package_folder_path_for_validator / MS_TRANSFORM_FOLDER_NAME / MS_MAPPINGS_FOLDER_NAME,
        package_folder_path_for_validator / MS_TRANSFORM_FOLDER_NAME / MS_RESOURCES_FOLDER_NAME,
        package_folder_path_for_validator / MS_TRANSFORM_FOLDER_NAME / MS_CONCEPTUAL_MAPPING_FILE_NAME,
        package_folder_path_for_validator / MS_TEST_DATA_FOLDER_NAME,
    ]
    return assert_path(mandatory_paths_l1)


def validate_mapping_suite_structure_lv2(package_folder_path_for_validator: pathlib.Path):
    """
        Check if the expanded mapping suite structure is in place
    """
    mandatory_paths_l2 = [
        package_folder_path_for_validator / MS_METADATA_FILE_NAME,
        package_folder_path_for_validator / MS_VALIDATE_FOLDER_NAME,
        package_folder_path_for_validator / MS_VALIDATE_FOLDER_NAME / MS_SPARQL_FOLDER_NAME,
        package_folder_path_for_validator / MS_VALIDATE_FOLDER_NAME / MS_SHACL_FOLDER_NAME,
    ]
    return assert_path(mandatory_paths_l2)


def validate_mapping_suite_structure_lv3(package_folder_path_for_validator: pathlib.Path):
    """
        Check if the transformed and validated mapping suite structure is in place.
    """
    mandatory_paths_l3 = [
        package_folder_path_for_validator / MS_OUTPUT_FOLDER_NAME,
    ]

    for item in (package_folder_path_for_validator / MS_OUTPUT_FOLDER_NAME).iterdir():
        if item.is_dir():
            mandatory_paths_l3 += item
            mandatory_paths_l3 += item / MS_TEST_SUITE_REPORT

    return assert_path(mandatory_paths_l3)


def check_metadata_consistency(package_folder_path_for_validator: pathlib.Path,
                               conceptual_mappings_file_path) -> bool:

    """
        Read the conceptual mapping XSLX and the metadata.json and compare the contents,
        in particular paying attention to the mapping suite version and the ontology version.
    """
    # if not validate_mapping_suite_structure_lv2(package_folder_path_for_validator):
    #     return False
    conceptual_mappings_document = mapping_suite_read_metadata(conceptual_mappings_file_path=conceptual_mappings_file_path)
    mapping_version = [val for val in conceptual_mappings_document.values()][4][0]
    epo_version = [val for val in conceptual_mappings_document.values()][5][0]

    package_metadata_path = package_folder_path_for_validator / MS_METADATA_FILE_NAME
    package_metadata_content = package_metadata_path.read_text(encoding="utf-8")
    package_metadata = json.loads(package_metadata_content)
    package_metadata['metadata_constraints'] = MetadataConstraints(**package_metadata['metadata_constraints'])
    metadata_version = [val for val in package_metadata.values()][3]
    metadata_ontology_version = [val for val in package_metadata.values()][4]

    if mapping_version > metadata_version and epo_version > metadata_ontology_version:
        return True
    else:
        raise TypeError('Not the same value between metadata.json [version, epo version] and conceptual_mapping_file [version, ontology_version')




