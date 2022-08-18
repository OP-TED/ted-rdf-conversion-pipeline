
import pathlib
import shutil
import tempfile
from pathlib import Path


from ted_sws.event_manager.adapters.event_handler_config import ConsoleLoggerConfig
from ted_sws.event_manager.services.logger_from_context import get_env_logger
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.model.event_message import EventMessage
from ted_sws.data_manager.adapters.mapping_suite_repository import MS_TRANSFORM_FOLDER_NAME, \
    MS_VALIDATE_FOLDER_NAME, MS_OUTPUT_FOLDER_NAME
from ted_sws.mapping_suite_processor.adapters.mapping_suite_structure_checker import \
    validate_mapping_suite_structure_lv2, MS_METADATA_FILE_NAME, validate_mapping_suite_structure_lv1, \
    validate_mapping_suite_structure_lv3, check_metadata_consistency
from ted_sws.mapping_suite_processor.services.conceptual_mapping_reader import mapping_suite_read_metadata

SHACL_EPO = "shacl_epo.htlm"
SPARQL_CM_ASSERTIONS = "sparql_cm_assertions.html"
KEY_VERSION = "Mapping Version"
KEY_EPO = "EPO version"
logger = get_env_logger(EventLogger(ConsoleLoggerConfig(name="LOGGER")))


def test_validate_mapping_suite_structure_lv1(package_folder_path_for_validator):
    with tempfile.TemporaryDirectory() as temp_folder:
        shutil.copytree(package_folder_path_for_validator, temp_folder, dirs_exist_ok=True)
        assert validate_mapping_suite_structure_lv1(Path(temp_folder))

    with tempfile.TemporaryDirectory() as temp_folder:
         shutil.copytree(package_folder_path_for_validator, temp_folder, dirs_exist_ok=True)
         shutil.rmtree((Path(temp_folder) / MS_TRANSFORM_FOLDER_NAME).resolve(), ignore_errors=True)
    if not (Path(temp_folder) / MS_TRANSFORM_FOLDER_NAME).resolve():
        logger.debug(EventMessage(message="SOME_MESSAGE"))
        validate_mapping_suite_structure_lv1(Path(temp_folder))


def test_validate_mapping_suite_structure_lv2(package_folder_path_for_validator):
    with tempfile.TemporaryDirectory() as temp_folder:
        shutil.copytree(package_folder_path_for_validator, temp_folder, dirs_exist_ok=True)
        assert validate_mapping_suite_structure_lv2(Path(temp_folder))

    with tempfile.TemporaryDirectory() as temp_folder:
        shutil.copytree(package_folder_path_for_validator, temp_folder, dirs_exist_ok=True)
        shutil.rmtree((Path(temp_folder) / MS_VALIDATE_FOLDER_NAME).resolve(), ignore_errors=True)
    if not (Path(temp_folder) / MS_VALIDATE_FOLDER_NAME).resolve():
        logger.debug(EventMessage(message="SOME_MESSAGE"))
        validate_mapping_suite_structure_lv2(Path(temp_folder))


def test_validate_mapping_suite_structure_lv3(package_folder_path_for_validator):
    with tempfile.TemporaryDirectory() as temp_folder:
        shutil.copytree(package_folder_path_for_validator, temp_folder, dirs_exist_ok=True)
        assert validate_mapping_suite_structure_lv3(Path(temp_folder))

    with tempfile.TemporaryDirectory() as temp_folder:
        shutil.copytree(package_folder_path_for_validator, temp_folder, dirs_exist_ok=True)
        shutil.rmtree((Path(temp_folder) / MS_OUTPUT_FOLDER_NAME).resolve(), ignore_errors=True)
    if not (Path(temp_folder) / MS_OUTPUT_FOLDER_NAME).resolve():
        logger.debug(EventMessage(message="SOME_MESSAGE"))
        validate_mapping_suite_structure_lv2(Path(temp_folder))


def test_check_metadata_consistency(package_folder_path_for_validator, conceptual_mappings_file_path):

    check_metadata_consistency(conceptual_mappings_file_path=conceptual_mappings_file_path,
                               package_folder_path_for_validator=package_folder_path_for_validator)

    conceptual_mappings_file = pathlib.Path(conceptual_mappings_file_path)
    assert conceptual_mappings_file.exists()
    metadata_file = pathlib.Path(package_folder_path_for_validator / MS_METADATA_FILE_NAME)
    assert metadata_file.exists()
    mapping_version = mapping_suite_read_metadata(conceptual_mappings_file_path=conceptual_mappings_file_path)
    assert KEY_VERSION in mapping_version
    assert KEY_EPO in mapping_version

