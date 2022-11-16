import pathlib
import tempfile
from typing import List

from pymongo import MongoClient

from ted_sws import config
from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.core.model.notice import Notice
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem, \
    MappingSuiteRepositoryMongoDB
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.event_manager.services.log import log_mapping_suite_info, log_mapping_suite_error
from ted_sws.mapping_suite_processor.adapters.github_package_downloader import GitHubMappingSuitePackageDownloader
from ted_sws.mapping_suite_processor.services.mapping_suite_digest_service import \
    update_digest_api_address_for_mapping_suite
from ted_sws.mapping_suite_processor.services.mapping_suite_validation_service import validate_mapping_suite, \
    get_mapping_suite_id_from_file_system

CONCEPTUAL_MAPPINGS_ASSERTIONS = "cm_assertions"
SHACL_SHAPE_INJECTION_FOLDER = "ap_data_shape"
SHACL_SHAPE_RESOURCES_FOLDER = "shacl_shapes"
SHACL_SHAPE_FILE_NAME = "ePO_shacl_shapes.rdf"
MAPPING_FILES_RESOURCES_FOLDER = "mapping_files"
SPARQL_QUERIES_RESOURCES_FOLDER = "queries"
SPARQL_QUERIES_INJECTION_FOLDER = "business_queries"
PROD_ARCHIVE_SUFFIX = "prod"
DEMO_ARCHIVE_SUFFIX = "demo"
DEFAULT_BRANCH_NAME = "main"
MAPPING_SUITE_UNKNOWN_ID = "unknown_mapping_suite_id"


def mapping_suite_processor_load_package_in_mongo_db(mapping_suite_package_path: pathlib.Path,
                                                     mongodb_client: MongoClient,
                                                     load_test_data: bool = False,
                                                     git_last_commit_hash: str = None
                                                     ) -> List[str]:
    """
        This feature allows you to upload a mapping suite package to MongoDB.
    :param mapping_suite_package_path:
    :param mongodb_client:
    :param load_test_data:
    :param git_last_commit_hash:
    :return:
    """

    mapping_suite_repository_path = mapping_suite_package_path.parent
    mapping_suite_package_name = mapping_suite_package_path.name
    mapping_suite_repository_in_file_system = MappingSuiteRepositoryInFileSystem(
        repository_path=mapping_suite_repository_path)
    mapping_suite_in_memory = mapping_suite_repository_in_file_system.get(reference=mapping_suite_package_name)

    update_digest_api_address_for_mapping_suite(mapping_suite_in_memory)

    if git_last_commit_hash is not None:
        mapping_suite_in_memory.git_latest_commit_hash = git_last_commit_hash
    result_notice_ids = []
    if load_test_data:
        tests_data = mapping_suite_in_memory.transformation_test_data.test_data
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        for test_data in tests_data:
            notice_id = test_data.file_name.split(".")[0]
            notice_repository.add(notice=Notice(ted_id=notice_id,
                                                xml_manifestation=XMLManifestation(object_data=test_data.file_content)))
            result_notice_ids.append(notice_id)
    mapping_suite_repository_mongo_db = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_suite_repository_mongo_db.add(mapping_suite=mapping_suite_in_memory)
    return result_notice_ids


def mapping_suite_processor_from_github_expand_and_load_package_in_mongo_db(mongodb_client: MongoClient,
                                                                            mapping_suite_package_name: str = None,
                                                                            load_test_data: bool = False,
                                                                            branch_or_tag_name: str = None,
                                                                            github_repository_url: str = None
                                                                            ) -> List[str]:
    """
        This feature is intended to download a mapping_suite_package from GitHub and process it for upload to MongoDB.
    :param github_repository_url:
    :param branch_or_tag_name:
    :param mapping_suite_package_name:
    :param mongodb_client:
    :param load_test_data:
    :return:
    """
    branch_or_tag_name = branch_or_tag_name if branch_or_tag_name else DEFAULT_BRANCH_NAME
    github_repository_url = github_repository_url if github_repository_url else config.GITHUB_TED_SWS_ARTEFACTS_URL
    mapping_suite_package_downloader = GitHubMappingSuitePackageDownloader(
        github_repository_url=github_repository_url, branch_or_tag_name=branch_or_tag_name)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir_path = pathlib.Path(tmp_dir)
        git_last_commit_hash = mapping_suite_package_downloader.download(output_mapping_suite_package_path=tmp_dir_path)

        mapping_suite_package_paths = [
            tmp_dir_path / mapping_suite_package_name] if mapping_suite_package_name else list(tmp_dir_path.iterdir())
        result_notice_ids = []
        for mapping_suite_package_path in mapping_suite_package_paths:
            validation_result = validate_mapping_suite(mapping_suite_path=mapping_suite_package_path)
            mapping_suite_id = get_mapping_suite_id_from_file_system(mapping_suite_path=mapping_suite_package_path)
            if mapping_suite_id is None:
                log_mapping_suite_error(
                    message="Invalid mapping suite metadata, can't read mapping suite identifier!",
                    mapping_suite_id=MAPPING_SUITE_UNKNOWN_ID)
            elif validation_result:
                log_mapping_suite_info(
                    message=f"Mapping suite with id={mapping_suite_id} is valid for loading in MongoDB!",
                    mapping_suite_id=mapping_suite_id)
                result_notice_ids.extend(mapping_suite_processor_load_package_in_mongo_db(
                    mapping_suite_package_path=mapping_suite_package_path,
                    mongodb_client=mongodb_client,
                    load_test_data=load_test_data,
                    git_last_commit_hash=git_last_commit_hash
                ))
                log_mapping_suite_info(
                    message=f"Mapping suite with id={mapping_suite_id} loaded with success in MongoDB!",
                    mapping_suite_id=mapping_suite_id)
            else:
                log_mapping_suite_error(
                    message=f"Mapping suite with id={mapping_suite_id} is invalid for loading in MongoDB!",
                    mapping_suite_id=mapping_suite_id)

    return result_notice_ids
