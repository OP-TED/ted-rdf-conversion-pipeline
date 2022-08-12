import pathlib
from typing import List

from ted_sws.event_manager.adapters.event_handler_config import CLILoggerConfig
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.model.event_message import EventMessage
from ted_sws.event_manager.services.logger_from_context import get_env_logger

MS_METADATA_FILE_NAME = "metadata.json"
MS_TRANSFORM_FOLDER_NAME = "transformation"
MS_MAPPINGS_FOLDER_NAME = "mappings"
MS_RESOURCES_FOLDER_NAME = "resources"
MS_VALIDATE_FOLDER_NAME = "validation"
MS_SHACL_FOLDER_NAME = "shacl"
MS_SPARQL_FOLDER_NAME = "sparql"
MS_TEST_DATA_FOLDER_NAME = "test_data"
MS_CONCEPTUAL_MAPPING_FILE_NAME = "conceptual_mappings.xlsx"
MS_OUTPUT_FOLDER_NAME = "output"
MS_TEST_SUITE_REPORT = "test_suite_report"
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


def check_metadata_consistency(package_folder_path_for_validator: pathlib.Path):
    """
        Read the conceptual mapping XSLX and the metadata.json and compare the contents,
        in particular paying attention to the mapping suite version and the ontology version.
    """
    if not validate_mapping_suite_structure_lv2(package_folder_path_for_validator):
        return False

    ...
