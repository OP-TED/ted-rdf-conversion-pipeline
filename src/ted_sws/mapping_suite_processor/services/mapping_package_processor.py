import pathlib
import tempfile
from typing import List

from pymongo import MongoClient

# WORKAROUND: Disable __del__ in MSSDK's MongoDBRepository to prevent premature client closure  
# The MSSDK MongoDBRepository closes the MongoClient in __del__, but it doesn't own the client.
# When the repository is garbage collected, it closes the shared client unexpectedly.
from mapping_suite_sdk.core.adapters.repository import MongoDBRepository as _MSSKDMongoDBRepository
if hasattr(_MSSKDMongoDBRepository, '__del__'):
    delattr(_MSSKDMongoDBRepository, '__del__')

from src.ted_sws import config
from src.ted_sws.core.model.manifestation import XMLManifestation
from src.ted_sws.core.model.notice import Notice
from src.ted_sws.data_manager.adapters.mapping_package_repository import MappingPackageRepositoryMongoDB
from src.ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryMongoDB
from src.ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from src.ted_sws.event_manager.services.log import log_mapping_package_info, log_mapping_package_error, \
    log_technical_info, log_technical_warning
from src.ted_sws.mapping_suite_processor.adapters.github_ms_project_downloader import GitHubMappingSuiteDownloader
from src.ted_sws.mapping_suite_processor.services import MappingPackageProcessorServiceError
from src.ted_sws.mapping_suite_processor.services.mapping_package_digest_service import \
    update_digest_api_address_for_mapping_package
# TODO: DEPRECATE/REMOVE once tests updated for MSSDK validation
from src.ted_sws.mapping_suite_processor.services.mapping_package_validation_service import validate_mapping_package, \
    get_mapping_package_id_from_file_system

from mapping_suite_sdk.mapping_suite.services.load_mapping_suite import load_mapping_suite_from_folder
from mapping_suite_sdk.tools.services.convert_mapping_package import load_mapping_package_from_folder
from mapping_suite_sdk.core.adapters.version_detector import detect_mapping_package_version
from mapping_suite_sdk.mapping_package_v2.services.validate_mapping_package_v2 import validate_mapping_package_v2

from src.ted_sws.core.model.transform import MappingPackage

SHACL_SHAPE_INJECTION_FOLDER = "ap_data_shape"
SHACL_SHAPE_RESOURCES_FOLDER = "shacl_shapes"
SHACL_SHAPE_FILE_NAME = "ePO_shacl_shapes.ttl"
MAPPING_FILES_RESOURCES_FOLDER = "mapping_files"
SPARQL_QUERIES_RESOURCES_FOLDER = "queries"
SPARQL_QUERIES_INJECTION_FOLDER = "business_queries"
PROD_ARCHIVE_SUFFIX = "prod"
DEMO_ARCHIVE_SUFFIX = "demo"
DEFAULT_BRANCH_NAME = "main"
MAPPING_PACKAGE_UNKNOWN_ID = "unknown_mapping_package_id"


def mapping_package_processor_load_package_in_mongo_db(
    package: MappingPackage,
    mongodb_client: MongoClient,
    load_test_data: bool = False,
    git_last_commit_hash: str = None
) -> List[str]:
    """Load a mapping package to MongoDB.
    
    Supports both legacy MappingPackage model and MSSDK models (V1, V2, V3, V3L).
    
    Args:
        package: The mapping package (legacy or MSSDK model)
        mongodb_client: MongoDB client instance
        load_test_data: Whether to load test data as notices
        git_last_commit_hash: Optional git commit hash to store
        
    Returns:
        List of notice IDs that were loaded (if load_test_data=True)
    """
    # Update digest
    # FIXME refactor for MSSDK transformation rule set structure, currently BROKEN
    update_digest_api_address_for_mapping_package(package)

    # Update git hash if provided and field exists
    if git_last_commit_hash is not None:
        package.git_latest_commit_hash = git_last_commit_hash
    result_notice_ids = []
    
    # Load test data if requested
    # FIXME refactor for MSSDK's two-level test data structure, currently BROKEN
    if load_test_data:
        tests_data = package.transformation_test_data.test_data
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        for test_data in tests_data:
            notice_id = test_data.file_name.split(".")[0]
            notice = Notice(ted_id=notice_id)
            notice.set_xml_manifestation(XMLManifestation(object_data=test_data.file_content))
            notice_repository.add(notice=notice)
            result_notice_ids.append(notice_id)
    mapping_package_repository_mongo_db = MappingPackageRepositoryMongoDB(mongodb_client=mongodb_client)
    # FIXME: will throw pymongo.errors.DuplicateKeyError if package with same id exists
    mapping_package_repository_mongo_db.add(package)
    return result_notice_ids


def load_mapping_suite_and_packages_from_github_to_mongo_db(mongodb_client: MongoClient,
                                                            mapping_package_name: str = None,
                                                            load_test_data: bool = False,
                                                            branch_or_tag_name: str = None,
                                                            github_repository_url: str = None
                                                            ) -> List[str]:
    """
    This feature is intended to download a mapping project from GitHub and process it for upload to MongoDB.
    :param github_repository_url:
    :param branch_or_tag_name:
    :param mapping_package_name:
    :param mongodb_client:
    :param load_test_data:
    :return:
    """
    branch_or_tag_name = branch_or_tag_name if branch_or_tag_name else DEFAULT_BRANCH_NAME
    github_repository_url = github_repository_url if github_repository_url else config.GITHUB_TED_SWS_ARTEFACTS_URL
    mapping_package_downloader = GitHubMappingSuiteDownloader(
        github_repository_url=github_repository_url, branch_or_tag_name=branch_or_tag_name)
    mappings_dir_name = mapping_package_downloader.MAPPINGS_DIR_NAME
    ms_config_dir_name = mapping_package_downloader.MS_CONFIG_DIR_NAME
    ms_config_file_name = mapping_package_downloader.MS_CONFIG_FILE_NAME
    log_technical_info(
        message=f"Using mappings directory '{mappings_dir_name}', config directory '{ms_config_dir_name}' and config file '{ms_config_file_name}'")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir_path = pathlib.Path(tmp_dir)
        mappings_dir_path = tmp_dir_path / mappings_dir_name
        ms_config_dir_path = tmp_dir_path / ms_config_dir_name
        ms_config_file_path = ms_config_dir_path / ms_config_file_name
        log_technical_info(
            message=f"Downloading mapping suite from GitHub repository '{github_repository_url}' on branch/tag '{branch_or_tag_name}'")
        git_last_commit_hash = mapping_package_downloader.download(output_project_path=tmp_dir_path)

        # load project config if available
        if ms_config_file_path.is_file():
            log_technical_info(message=f"Mapping suite config found at '{ms_config_file_path}'")
            mapping_suite = load_mapping_suite_from_folder(mapping_suite_folder_path=tmp_dir_path)
            log_technical_info(
                message=f"Mapping suite config '{mapping_suite.id}' loaded from folder with success")
            mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
            mapping_suite_repository.add(mapping_suite)
            log_technical_info(
                message=f"Mapping suite config '{mapping_suite.id}' saved with success")
        elif ms_config_dir_path.is_dir():
            log_technical_warning(
                message=f"Mapping suite config directory found at '{ms_config_dir_path}' but MISSING config file '{ms_config_file_name}'")
        else:
            log_technical_warning(
                message=f"No mapping suite config found at '{ms_config_dir_path}'")

        # continue loading mapping packages
        mapping_package_paths = [
            mappings_dir_path / mapping_package_name ] if mapping_package_name else list(mappings_dir_path.iterdir())
        result_notice_ids = []
        for mapping_package_path in mapping_package_paths:
            detected_version = detect_mapping_package_version(mapping_package_path)
            log_technical_info(
                message=f"Mapping package version detected '{detected_version}'")
            # TODO once MSSDK detection and conversion works, do conversion here based on detected version
            mssdk_package = load_mapping_package_from_folder("v2", mapping_package_path)
            log_technical_info(
                message=f"Mapping package '{mssdk_package.id}' loaded from folder with success")            
            validation_result = validate_mapping_package_v2(mssdk_package)
            mapping_package = _convert_to_mapping_package(mssdk_package)
            if validation_result:
                log_mapping_package_info(
                    message=f"Mapping package with id={mapping_package.id} is valid for loading in MongoDB!",
                    mapping_package_id=mapping_package.id)
                result_notice_ids.extend(mapping_package_processor_load_package_in_mongo_db(
                    package=mapping_package,
                    mongodb_client=mongodb_client,
                    load_test_data=load_test_data,
                    git_last_commit_hash=git_last_commit_hash
                ))
                log_mapping_package_info(
                    message=f"Mapping package with id={mapping_package.id} loaded with success in MongoDB!",
                    mapping_package_id=mapping_package.id)
            else:
                error_msg = f"Mapping package with id={mapping_package.id} is invalid for loading in MongoDB!"
                log_mapping_package_error(
                    message=error_msg,
                    mapping_package_id=mapping_package.id)
                raise MappingPackageProcessorServiceError(error_msg)

    return result_notice_ids


def _convert_to_mapping_package(mssdk_package) -> MappingPackage:
    """Convert MSSDK package to extended MappingPackage."""
    data = mssdk_package.model_dump(exclude={'test_results'})
    return MappingPackage(**data)
