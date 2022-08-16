import json
import pathlib
import shutil
import tempfile
from pathlib import Path

import pytest

from ted_sws.core.model.transform import MetadataConstraints
from ted_sws.data_manager.adapters.mapping_suite_repository import MS_TRANSFORM_FOLDER_NAME, \
    MS_CONCEPTUAL_MAPPING_FILE_NAME, MS_VALIDATE_FOLDER_NAME, MS_OUTPUT_FOLDER_NAME
from ted_sws.mapping_suite_processor.adapters.mapping_suite_structure_checker import \
    validate_mapping_suite_structure_lv2, MS_METADATA_FILE_NAME, validate_mapping_suite_structure_lv1, \
    validate_mapping_suite_structure_lv3, check_metadata_consistency


def test_validate_mapping_suite_structure_lv1(package_folder_path_for_validator):
    with tempfile.TemporaryDirectory() as temp_folder:
        shutil.copytree(package_folder_path_for_validator, temp_folder, dirs_exist_ok=True)
        assert validate_mapping_suite_structure_lv1(Path(temp_folder))

    with tempfile.TemporaryDirectory() as temp_folder:
        shutil.copytree(package_folder_path_for_validator, temp_folder, dirs_exist_ok=True)
        shutil.rmtree((Path(temp_folder) / MS_TRANSFORM_FOLDER_NAME).resolve(), ignore_errors=True)
        with pytest.raises(AssertionError):
            validate_mapping_suite_structure_lv1(Path(temp_folder))

    with tempfile.TemporaryDirectory() as temp_folder:
        shutil.copytree(package_folder_path_for_validator, temp_folder, dirs_exist_ok=True)
        shutil.rmtree((Path(temp_folder) / MS_TRANSFORM_FOLDER_NAME / MS_CONCEPTUAL_MAPPING_FILE_NAME).unlink(
            missing_ok=True), ignore_errors=True)
        with pytest.raises(AssertionError):
            validate_mapping_suite_structure_lv1(Path(temp_folder))


def test_validate_mapping_suite_structure_lv2(package_folder_path_for_validator):
    with tempfile.TemporaryDirectory() as temp_folder:
        shutil.copytree(package_folder_path_for_validator, temp_folder, dirs_exist_ok=True)
        assert validate_mapping_suite_structure_lv2(Path(temp_folder))

    with tempfile.TemporaryDirectory() as temp_folder:
        shutil.copytree(package_folder_path_for_validator, temp_folder, dirs_exist_ok=True)
        shutil.rmtree((Path(temp_folder) / MS_VALIDATE_FOLDER_NAME).resolve(), ignore_errors=True)
        with pytest.raises(AssertionError):
            validate_mapping_suite_structure_lv2(Path(temp_folder))


def test_validate_mapping_suite_structure_lv3(package_folder_path_for_validator):
    with tempfile.TemporaryDirectory() as temp_folder:
        shutil.copytree(package_folder_path_for_validator, temp_folder, dirs_exist_ok=True)
        assert validate_mapping_suite_structure_lv3(Path(temp_folder))

    with tempfile.TemporaryDirectory() as temp_folder:
        shutil.copytree(package_folder_path_for_validator, temp_folder, dirs_exist_ok=True)
        shutil.rmtree((Path(temp_folder) / MS_OUTPUT_FOLDER_NAME).resolve(), ignore_errors=True)
        with pytest.raises(AssertionError):
            validate_mapping_suite_structure_lv3(Path(temp_folder))


def test_check_metadata_consistency(package_folder_path_for_validator, conceptual_mappings_file_path):
    """
        Read the conceptual mapping XSLX and the metadata.json and compare the contents,
        in particular paying attention to the mapping suite version and the ontology version.
    """
    check_metadata_consistency(conceptual_mappings_file_path=conceptual_mappings_file_path,
                               package_folder_path_for_validator=package_folder_path_for_validator)





