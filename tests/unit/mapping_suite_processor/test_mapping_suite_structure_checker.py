import os
import pathlib
import shutil
import tempfile
from pathlib import Path

from ted_sws.event_manager.adapters.event_handler_config import ConsoleLoggerConfig, CLILoggerConfig
from ted_sws.event_manager.services.logger_from_context import get_env_logger
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.data_manager.adapters.mapping_suite_repository import MS_TRANSFORM_FOLDER_NAME, \
    MS_VALIDATE_FOLDER_NAME, MS_OUTPUT_FOLDER_NAME, MS_RESOURCES_FOLDER_NAME, MS_TEST_DATA_FOLDER_NAME, \
    MS_CONCEPTUAL_MAPPING_FILE_NAME
from ted_sws.mapping_suite_processor.adapters.mapping_suite_structure_checker import \
    MS_METADATA_FILE_NAME, MappingSuiteStructureValidator
from ted_sws.mapping_suite_processor.services.conceptual_mapping_reader import mapping_suite_read_metadata
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.model.event_message import EventMessage

SHACL_EPO = "shacl_epo.htlm"
SPARQL_CM_ASSERTIONS = "sparql_cm_assertions.html"
KEY_VERSION = "Mapping Version"
KEY_EPO = "EPO version"
# logger = get_env_logger(EventLogger(ConsoleLoggerConfig(name="LOGGER")), is_cli=True)
logger = get_env_logger(EventLogger(CLILoggerConfig()), is_cli=True)


def test_validate_core_structure(package_folder_path_for_validator, caplog):
    with tempfile.TemporaryDirectory() as temp_folder:
        shutil.copytree(package_folder_path_for_validator, temp_folder, dirs_exist_ok=True)
        mapping_suite_validator = MappingSuiteStructureValidator(temp_folder)

        assert mapping_suite_validator.validate_core_structure()

        print("K :: ", caplog.text)
        shutil.rmtree(Path(temp_folder))

        assert not mapping_suite_validator.validate_core_structure()
        assert caplog.text.count("Path not found") >= 4
        assert caplog.text.count(MS_TRANSFORM_FOLDER_NAME) >= 3
        assert MS_RESOURCES_FOLDER_NAME in caplog.text
        assert MS_CONCEPTUAL_MAPPING_FILE_NAME in caplog.text
        assert MS_TEST_DATA_FOLDER_NAME in caplog.text


def test_validate_expanded_structure(package_folder_path_for_validator, caplog):
    with tempfile.TemporaryDirectory() as temp_folder:
        shutil.copytree(package_folder_path_for_validator, temp_folder, dirs_exist_ok=True)
        mapping_suite_validator = MappingSuiteStructureValidator(temp_folder)
        assert mapping_suite_validator.validate_expanded_structure()
        print("K2 :: ", caplog.text)

        metadata_path = (pathlib.Path(temp_folder) / MS_METADATA_FILE_NAME)
        with open(metadata_path, 'r+') as f:
            f.truncate(0)
        assert metadata_path.stat().st_size == 0
        mapping_suite_validator.validate_expanded_structure()
        assert "File is empty" in caplog.text
        assert MS_METADATA_FILE_NAME in caplog.text


def test_validate_output_structure(package_folder_path_for_validator, caplog):
    with tempfile.TemporaryDirectory() as temp_folder:
        shutil.copytree(package_folder_path_for_validator, temp_folder, dirs_exist_ok=True)
        mapping_suite_validator = MappingSuiteStructureValidator(temp_folder)
        assert mapping_suite_validator.validate_output_structure()
        print("K3 :: ", caplog.text)

        dirpath = (pathlib.Path(temp_folder) / MS_OUTPUT_FOLDER_NAME)
        for filename in os.listdir(dirpath):
            filepath = os.path.join(dirpath, filename)
            try:
                shutil.rmtree(filepath)
            except OSError:
                os.remove(filepath)
        mapping_suite_validator.validate_output_structure()
        assert "Folder is empty" in caplog.text
        assert MS_OUTPUT_FOLDER_NAME in caplog.text


def test_check_metadata_consistency(package_folder_path_for_validator):
    with tempfile.TemporaryDirectory() as temp_folder:
        shutil.copytree(package_folder_path_for_validator, temp_folder, dirs_exist_ok=True)
        mapping_suite_validator = MappingSuiteStructureValidator(temp_folder)
        mapping_suite_validator.check_metadata_consistency()
        conceptual_mappings_file_path = (pathlib.Path(temp_folder) / MS_TRANSFORM_FOLDER_NAME / MS_CONCEPTUAL_MAPPING_FILE_NAME)
        conceptual_mappings_file = pathlib.Path(conceptual_mappings_file_path)
        assert conceptual_mappings_file.exists()
        metadata_file = pathlib.Path(package_folder_path_for_validator / MS_METADATA_FILE_NAME)
        assert metadata_file.exists()
        mapping_version = mapping_suite_read_metadata(conceptual_mappings_file_path=conceptual_mappings_file_path)
        assert KEY_VERSION in mapping_version
        assert KEY_EPO in mapping_version
