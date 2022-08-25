import hashlib
import json
import os
import pathlib
from typing import List, Union

from ted_sws.core.model.transform import MetadataConstraints
from ted_sws.data_manager.adapters.mapping_suite_repository import MS_TRANSFORM_FOLDER_NAME, MS_TEST_DATA_FOLDER_NAME, \
    MS_CONCEPTUAL_MAPPING_FILE_NAME, MS_RESOURCES_FOLDER_NAME, MS_MAPPINGS_FOLDER_NAME, MS_METADATA_FILE_NAME, \
    MS_VALIDATE_FOLDER_NAME, MS_SPARQL_FOLDER_NAME, MS_SHACL_FOLDER_NAME, MS_OUTPUT_FOLDER_NAME
from ted_sws.event_manager.adapters.event_handler_config import ConsoleLoggerConfig
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.model.event_message import EventMessage
from ted_sws.event_manager.services.logger_from_context import get_env_logger
from ted_sws.mapping_suite_processor.adapters.mapping_suite_hasher import MappingSuiteHasher
from ted_sws.mapping_suite_processor.services.conceptual_mapping_generate_metadata import VERSION_FIELD, \
    MAPPING_SUITE_HASH, VERSION_KEY
from ted_sws.mapping_suite_processor.services.conceptual_mapping_reader import mapping_suite_read_metadata

SHACL_KEYWORD = "shacl"
SPARQL_KEYWORD = "sparql"


class MappingSuiteStructureValidator:

    def __init__(self, mapping_suite_path: Union[pathlib.Path, str]):
        self.mapping_suite_path = pathlib.Path(mapping_suite_path)
        self.is_valid = True
        self.logger = get_env_logger(EventLogger(ConsoleLoggerConfig(name="MappingSuiteStructureValidator")),
                                     is_cli=True)

    def assert_path(self, assertion_path_list: List[pathlib.Path]) -> bool:
        """
            Validate whether the given path exists and is non empty.
        """
        for path_item in assertion_path_list:
            message_path_not_found = f"Path not found: {path_item}"
            if not path_item.exists():
                self.logger.error(event_message=EventMessage(message=message_path_not_found))
                self.is_valid = False
                continue

            if path_item.is_dir():
                message_folder_empty = f"Folder is empty: {path_item}"
                if not any(path_item.iterdir()):
                    self.logger.error(event_message=EventMessage(message=message_folder_empty))
                    self.is_valid = False
            else:
                message_file_is_empty = f"File is empty: {path_item}"
                if not path_item.stat().st_size > 0:
                    self.logger.error(event_message=EventMessage(message=message_file_is_empty))
                    self.is_valid = False

        return self.is_valid

    def validate_core_structure(self) -> bool:
        """
            Check whether the core mapping suite structure is in place.
        """
        mandatory_paths_l1 = [
            self.mapping_suite_path / MS_TRANSFORM_FOLDER_NAME,
            self.mapping_suite_path / MS_TRANSFORM_FOLDER_NAME / MS_MAPPINGS_FOLDER_NAME,
            self.mapping_suite_path / MS_TRANSFORM_FOLDER_NAME / MS_RESOURCES_FOLDER_NAME,
            self.mapping_suite_path / MS_TRANSFORM_FOLDER_NAME / MS_CONCEPTUAL_MAPPING_FILE_NAME,
            self.mapping_suite_path / MS_TEST_DATA_FOLDER_NAME,
        ]
        return self.assert_path(mandatory_paths_l1)

    def validate_expanded_structure(self) -> bool:
        """
            Check if the expanded mapping suite structure is in place
        """
        mandatory_paths_l2 = [
            self.mapping_suite_path / MS_METADATA_FILE_NAME,
            self.mapping_suite_path / MS_VALIDATE_FOLDER_NAME,
            self.mapping_suite_path / MS_VALIDATE_FOLDER_NAME / MS_SPARQL_FOLDER_NAME,
            self.mapping_suite_path / MS_VALIDATE_FOLDER_NAME / MS_SHACL_FOLDER_NAME,
        ]
        return self.assert_path(mandatory_paths_l2)

    def validate_output_structure(self) -> bool:
        """
            Check if the transformed and validated mapping suite structure is in place.
        """
        mandatory_paths_l3 = [
            self.mapping_suite_path / MS_OUTPUT_FOLDER_NAME,
        ]
        # TODO: refactor for in for in for with if then if then if
        for item in (self.mapping_suite_path / MS_OUTPUT_FOLDER_NAME).iterdir():
            if item.is_dir():
                for path in item.iterdir():
                    if path.is_dir():
                        for last_path in path.iterdir():
                            if SHACL_KEYWORD in os.path.basename(last_path) and SPARQL_KEYWORD in os.path.basename(
                                    last_path):
                                pass

        return self.assert_path(mandatory_paths_l3)

    def check_metadata_consistency(self) -> bool:

        """
            Read the conceptual mapping XSLX and the metadata.json and compare the contents,
            in particular paying attention to the mapping suite version and the ontology version.
        """

        conceptual_mappings_document = mapping_suite_read_metadata(
            conceptual_mappings_file_path=self.mapping_suite_path / MS_TRANSFORM_FOLDER_NAME / MS_CONCEPTUAL_MAPPING_FILE_NAME)
        conceptual_mappings_version = [val for val in conceptual_mappings_document.values()][4][0]
        conceptual_mappings_epo_version = [val for val in conceptual_mappings_document.values()][5][0]

        package_metadata_path = self.mapping_suite_path / MS_METADATA_FILE_NAME
        package_metadata_content = package_metadata_path.read_text(encoding="utf-8")
        package_metadata = json.loads(package_metadata_content)
        package_metadata['metadata_constraints'] = MetadataConstraints(**package_metadata['metadata_constraints'])
        metadata_version = [val for val in package_metadata.values()][3]
        metadata_epo_version = [val for val in package_metadata.values()][4]

        if conceptual_mappings_version> metadata_version and conceptual_mappings_epo_version> metadata_epo_version:
            pass
        else:
            self.is_valid = False
            # TODO: assert that this logged message is generated in the tests
            self.logger.error(event_message=EventMessage(
                message=f'Not the same value between metadata.json [version {metadata_version}, epo_version {metadata_epo_version}] and conceptual_mapping_file [version {conceptual_mappings_version}, epo_version {conceptual_mappings_epo_version}]'))

    def check_for_changes_by_version(self) -> bool:
        """
            This function check whether the mapping suite is well versioned and no changes detected.

            We want to ensure that:
             - the version in the metadata.json is the same as the version in the conceptual mappings
             - the version in always incremented
             - the changes in the mapping suite are detected by comparison to the hash in the metadata.json
             - the hash is bound to a version of the mapping suite written in the conceptual mappings
             - the version-bound-hash and the version are written in the metadata.json and are the same
             to the version in the conceptual mappings
        """
        conceptual_mapping_metadata = mapping_suite_read_metadata(
            conceptual_mappings_file_path=self.mapping_suite_path / MS_TRANSFORM_FOLDER_NAME / MS_CONCEPTUAL_MAPPING_FILE_NAME)

        metadata_json = json.loads((self.mapping_suite_path / MS_METADATA_FILE_NAME).read_text())

        version_in_cm = conceptual_mapping_metadata[VERSION_FIELD]

        mapping_suite_versioned_hash = MappingSuiteHasher(self.mapping_suite_path).hash_mapping_suite(
            with_version=version_in_cm)

        if mapping_suite_versioned_hash != metadata_json.get(MAPPING_SUITE_HASH):
            self.logger.error(event_message=EventMessage(
                message=f'The Mapping Suite hash digest ({mapping_suite_versioned_hash}) and the Version from the '
                        f'Conceptual Mappings ({version_in_cm}) '
                        f'does not correspond to the ones in the metadata.json file '
                        f'({metadata_json.get(MAPPING_SUITE_HASH)}, {metadata_json.get(VERSION_KEY)}). '
                        f'Consider increasing the version and regenerating the metadata.json'))
            self.is_valid = False

        return self.is_valid
