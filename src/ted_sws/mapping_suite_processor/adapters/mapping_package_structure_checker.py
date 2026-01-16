import pathlib
from typing import List, Union

from src.ted_sws.data_manager.adapters.mapping_package_repository import MS_TRANSFORM_FOLDER_NAME, MS_TEST_DATA_FOLDER_NAME, \
    MS_CONCEPTUAL_MAPPING_FILE_NAME, MS_RESOURCES_FOLDER_NAME, MS_MAPPINGS_FOLDER_NAME, MS_METADATA_FILE_NAME, \
    MS_VALIDATE_FOLDER_NAME, MS_SPARQL_FOLDER_NAME, MS_SHACL_FOLDER_NAME, MS_OUTPUT_FOLDER_NAME, MS_TEST_SUITE_REPORT, \
    mapping_package_read_version_from_metadata
from src.ted_sws.event_manager.model.event_message import EventMessage, EventMessageLogSettings
from src.ted_sws.event_manager.services.logger_from_context import get_console_logger
from src.ted_sws.mapping_suite_processor.adapters.mapping_package_hasher import MappingPackageHasher
from src.ted_sws.mapping_suite_processor.services.mapping_package_reader import mapping_package_read_metadata, \
    MAPPING_PACKAGE_HASH

SHACL_KEYWORD = "shacl"
SPARQL_KEYWORD = "sparql"
XPATH_KEYWORD = "xpath"

REPORTS_KEYWORDS = [SHACL_KEYWORD, SPARQL_KEYWORD, XPATH_KEYWORD]


class MappingPackageStructureValidator:
    reports_min_count: int = 3

    def __init__(self, mapping_package_path: Union[pathlib.Path, str]):
        self.mapping_package_path = pathlib.Path(mapping_package_path)
        self.logger = get_console_logger(name="MappingPackageStructureValidator")
        self.log_settings = EventMessageLogSettings(briefly=True)

    def assert_path(self, assertion_path_list: List[pathlib.Path]) -> bool:
        """
            Validate whether the given path exists and is non-empty.
        """
        success = True
        for path_item in assertion_path_list:
            message_path_not_found = f"Path not found: {path_item}"
            if not path_item.exists():
                self.logger.error(event_message=EventMessage(message=message_path_not_found),
                                  settings=self.log_settings)
                success = False
                continue

            if path_item.is_dir():
                message_folder_empty = f"Folder is empty: {path_item}"
                if not any(path_item.iterdir()):
                    self.logger.error(event_message=EventMessage(message=message_folder_empty),
                                      settings=self.log_settings)
                    success = False
            else:
                message_file_is_empty = f"File is empty: {path_item}"
                if path_item.stat().st_size <= 0:
                    self.logger.error(event_message=EventMessage(message=message_file_is_empty),
                                      settings=self.log_settings)
                    success = False

        return success

    def validate_core_structure(self) -> bool:
        """
            Check whether the core mapping package structure is in place.
        """
        self.logger.info(
            event_message=EventMessage(
                message="Check whether the core mapping package structure is in place."),
            settings=self.log_settings)
        mandatory_paths_l1 = [
            self.mapping_package_path / MS_TRANSFORM_FOLDER_NAME,
            self.mapping_package_path / MS_TRANSFORM_FOLDER_NAME / MS_MAPPINGS_FOLDER_NAME,
            self.mapping_package_path / MS_TRANSFORM_FOLDER_NAME / MS_RESOURCES_FOLDER_NAME,
            self.mapping_package_path / MS_TRANSFORM_FOLDER_NAME / MS_CONCEPTUAL_MAPPING_FILE_NAME,
            self.mapping_package_path / MS_TEST_DATA_FOLDER_NAME
        ]
        return self.assert_path(mandatory_paths_l1)

    def validate_expanded_structure(self) -> bool:
        """
            Check if the expanded mapping package structure is in place
        """
        self.logger.info(
            event_message=EventMessage(
                message="Check if the expanded mapping package structure is in place."),
            settings=self.log_settings)

        mandatory_paths_l2 = [
            self.mapping_package_path / MS_METADATA_FILE_NAME,
            self.mapping_package_path / MS_VALIDATE_FOLDER_NAME,
            self.mapping_package_path / MS_VALIDATE_FOLDER_NAME / MS_SPARQL_FOLDER_NAME,
            self.mapping_package_path / MS_VALIDATE_FOLDER_NAME / MS_SHACL_FOLDER_NAME,
        ]
        return self.assert_path(mandatory_paths_l2)

    def validate_output_structure(self) -> bool:
        """
            Check if the transformed and validated mapping package structure is in place.
        """

        self.logger.info(
            event_message=EventMessage(
                message="Check if the transformed and validated mapping package structure is in place."),
            settings=self.log_settings)

        success = True

        mandatory_paths_l3 = [
            self.mapping_package_path / MS_OUTPUT_FOLDER_NAME,
        ]

        success = success and self.assert_path(mandatory_paths_l3)
        if success:
            output_path = self.mapping_package_path / MS_OUTPUT_FOLDER_NAME
            notices_rdf_files_paths = [path for path in output_path.rglob("*.ttl") if path.is_file()]
            for notice_rdf_path in notices_rdf_files_paths:
                notice_path = notice_rdf_path.parent
                report_count = 0
                success = success and self.assert_path([notice_path / MS_TEST_SUITE_REPORT])
                if success:
                    for report in (notice_path / MS_TEST_SUITE_REPORT).iterdir():
                        if any(keyword in report.name for keyword in REPORTS_KEYWORDS):
                            report_count += 1
                    if report_count < self.reports_min_count:
                        self.logger.error(
                            event_message=EventMessage(message=f"{notice_path.stem} has missing validation reports."),
                            settings=self.log_settings)
                        success = False
                        break

        return success

    def check_for_changes_by_version(self) -> bool:
        """
            This function check whether the mapping package is well versioned and no changes detected.

            We want to ensure that:
             - the version in always incremented
             - the changes in the mapping package are detected by comparison to the hash in the metadata.json
             - the hash is bound to a version of the mapping package written in the conceptual mappings
             - the version-bound-hash and the version are written in the metadata.json and are the same
             to the version in the conceptual mappings
        """
        self.logger.info(
            event_message=EventMessage(
                message="Check whether the mapping package is well versioned and no changes detected."),
            settings=self.log_settings)
        success = True

        mapping_package_metadata = mapping_package_read_metadata(mapping_package_path=self.mapping_package_path)
        version = mapping_package_read_version_from_metadata(mapping_package_metadata)

        mapping_package_versioned_hash = MappingPackageHasher(
            mapping_package_path=self.mapping_package_path,
            mapping_package_metadata=mapping_package_metadata
        ).hash_mapping_package(with_version=version)

        if mapping_package_versioned_hash != mapping_package_metadata.get(MAPPING_PACKAGE_HASH):
            self.logger.error(
                event_message=EventMessage(
                    message=f'The Mapping Package hash digest ({mapping_package_versioned_hash}) '
                            f'does not correspond to the one in the metadata.json file '
                            f'({mapping_package_metadata.get(MAPPING_PACKAGE_HASH)}).'
                ),
                settings=self.log_settings
            )
            success = False

        return success

    def is_valid(self) -> bool:
        validate_core_structure: bool = self.validate_core_structure()
        validate_expanded_structure: bool = self.validate_expanded_structure()
        validate_output_structure: bool = self.validate_output_structure()
        check_for_changes_by_version: bool = self.check_for_changes_by_version()

        return \
                validate_core_structure \
                and validate_expanded_structure \
                and validate_output_structure \
                and check_for_changes_by_version
