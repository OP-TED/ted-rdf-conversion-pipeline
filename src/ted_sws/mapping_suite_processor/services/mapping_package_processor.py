import pathlib
import tempfile
from typing import List

from pymongo import MongoClient

from src.ted_sws import config
from src.ted_sws.core.model.manifestation import XMLManifestation
from src.ted_sws.core.model.notice import Notice
from src.ted_sws.data_manager.adapters.mapping_package_repository import MappingPackageRepositoryInFileSystem, \
    MappingPackageRepositoryMongoDB
from src.ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryMongoDB
from src.ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from src.ted_sws.event_manager.services.log import log_mapping_package_info, log_mapping_package_error, \
    log_technical_info, log_technical_warning
from src.ted_sws.mapping_suite_processor.adapters.github_ms_project_downloader import GitHubMappingSuiteDownloader
from src.ted_sws.mapping_suite_processor.services import MappingPackageProcessorServiceError
from src.ted_sws.mapping_suite_processor.services.mapping_package_digest_service import \
    update_digest_api_address_for_mapping_package
from src.ted_sws.mapping_suite_processor.services.mapping_package_validation_service import validate_mapping_package, \
    get_mapping_package_id_from_file_system

from mapping_suite_sdk.mapping_suite.services.load_mapping_suite import load_mapping_suite_from_folder


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


def mapping_package_processor_load_package_in_mongo_db(mapping_package_path: pathlib.Path,
                                                     mongodb_client: MongoClient,
                                                     load_test_data: bool = False,
                                                     git_last_commit_hash: str = None
                                                     ) -> List[str]:
    """
        This feature allows you to upload a mapping package package to MongoDB.
    :param mapping_package_path:
    :param mongodb_client:
    :param load_test_data:
    :param git_last_commit_hash:
    :return:
    """

    mapping_package_repository_path = mapping_package_path.parent
    mapping_package_name = mapping_package_path.name
    mapping_package_repository_in_file_system = MappingPackageRepositoryInFileSystem(
        repository_path=mapping_package_repository_path)
    mapping_package_in_memory = mapping_package_repository_in_file_system.get(reference=mapping_package_name)

    update_digest_api_address_for_mapping_package(mapping_package_in_memory)

    if git_last_commit_hash is not None:
        mapping_package_in_memory.git_latest_commit_hash = git_last_commit_hash
    result_notice_ids = []
    if load_test_data:
        tests_data = mapping_package_in_memory.transformation_test_data.test_data
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        for test_data in tests_data:
            notice_id = test_data.file_name.split(".")[0]
            notice = Notice(ted_id=notice_id)
            notice.set_xml_manifestation(XMLManifestation(object_data=test_data.file_content))
            notice_repository.add(notice=notice)
            result_notice_ids.append(notice_id)
    mapping_package_repository_mongo_db = MappingPackageRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_package_repository_mongo_db.add(mapping_package=mapping_package_in_memory)
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
    log_technical_info(
        message=f"Downloading mapping suite from GitHub repository '{github_repository_url}' on branch/tag '{branch_or_tag_name}'")
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
            validation_result = validate_mapping_package(mapping_package_path=mapping_package_path)
            mapping_package_id = get_mapping_package_id_from_file_system(mapping_package_path=mapping_package_path)
            if mapping_package_id is None:
                error_msg = "Invalid mapping package metadata, can't read mapping package identifier!"
                log_mapping_package_error(
                    message=error_msg,
                    mapping_package_id=MAPPING_PACKAGE_UNKNOWN_ID)
                raise MappingPackageProcessorServiceError(error_msg)
            elif validation_result:
                log_mapping_package_info(
                    message=f"Mapping package with id={mapping_package_id} is valid for loading in MongoDB!",
                    mapping_package_id=mapping_package_id)
                result_notice_ids.extend(mapping_package_processor_load_package_in_mongo_db(
                    mapping_package_path=mapping_package_path,
                    mongodb_client=mongodb_client,
                    load_test_data=load_test_data,
                    git_last_commit_hash=git_last_commit_hash
                ))
                log_mapping_package_info(
                    message=f"Mapping package with id={mapping_package_id} loaded with success in MongoDB!",
                    mapping_package_id=mapping_package_id)
            else:
                error_msg = f"Mapping package with id={mapping_package_id} is invalid for loading in MongoDB!"
                log_mapping_package_error(
                    message=error_msg,
                    mapping_package_id=mapping_package_id)
                raise MappingPackageProcessorServiceError(error_msg)

    return result_notice_ids
