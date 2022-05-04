import pathlib
import shutil
import tempfile

from pymongo import MongoClient

from ted_sws import config
from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.core.model.notice import Notice
from ted_sws.data_manager.adapters.mapping_suite_repository import TRANSFORM_PACKAGE_NAME, VALIDATE_PACKAGE_NAME, \
    SPARQL_PACKAGE_NAME, METADATA_FILE_NAME, RESOURCES_PACKAGE_NAME, SHACL_PACKAGE_NAME, TEST_DATA_PACKAGE_NAME, \
    MappingSuiteRepositoryInFileSystem, MappingSuiteRepositoryMongoDB
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.mapping_suite_processor.adapters.github_package_downloader import GitHubMappingSuitePackageDownloader
from ted_sws.mapping_suite_processor.services.conceptual_mapping_files_injection import \
    mapping_suite_processor_inject_resources, mapping_suite_processor_inject_shacl_shapes, \
    mapping_suite_processor_inject_sparql_queries
from ted_sws.mapping_suite_processor.services.conceptual_mapping_generate_metadata import \
    mapping_suite_processor_generate_metadata
from ted_sws.mapping_suite_processor.services.conceptual_mapping_generate_sparql_queries import \
    mapping_suite_processor_generate_sparql_queries
from ted_sws.resources import RESOURCES_PATH

CONCEPTUAL_MAPPINGS_FILE_NAME = "conceptual_mappings.xlsx"
CONCEPTUAL_MAPPINGS_ASSERTIONS = "cm_assertions"
SHACL_SHAPE_INJECTION_FOLDER = "ap_data_shape"
SHACL_SHAPE_RESOURCES_FOLDER = "shacl_shapes"
SHACL_SHAPE_FILE_NAME = "ePO_shacl_shapes.rdf"
MAPPING_FILES_RESOURCES_FOLDER = "mapping_files"
SPARQL_QUERIES_RESOURCES_FOLDER = "queries"
SPARQL_QUERIES_INJECTION_FOLDER = "business_queries"
PROD_ARCHIVE_SUFFIX = "prod"
DEMO_ARCHIVE_SUFFIX = "demo"


def mapping_suite_processor_zip_package(mapping_suite_package_path: pathlib.Path,
                                        prod_version: bool = False):
    """
        This function archives a package and puts a suffix in the name of the archive.
    :param mapping_suite_package_path:
    :param prod_version:
    :return:
    """
    archive_name_suffix = PROD_ARCHIVE_SUFFIX if prod_version else DEMO_ARCHIVE_SUFFIX
    tmp_folder_path = mapping_suite_package_path.parent / f"{mapping_suite_package_path.stem}-{archive_name_suffix}"
    output_archive_file_name = mapping_suite_package_path.parent / f"{mapping_suite_package_path.stem}-{archive_name_suffix}"
    shutil.copytree(mapping_suite_package_path, tmp_folder_path, dirs_exist_ok=True)
    if prod_version:
        shutil.rmtree(tmp_folder_path / TEST_DATA_PACKAGE_NAME)
    shutil.make_archive(str(output_archive_file_name), 'zip', tmp_folder_path)
    shutil.rmtree(tmp_folder_path)


def mapping_suite_processor_expand_package(mapping_suite_package_path: pathlib.Path):
    """
        This function reads data from conceptual_mappings.xlsx and expand provided package.
    :param mapping_suite_package_path:
    :return:
    """
    conceptual_mappings_file_path = mapping_suite_package_path / TRANSFORM_PACKAGE_NAME / CONCEPTUAL_MAPPINGS_FILE_NAME
    cm_sparql_folder_path = mapping_suite_package_path / VALIDATE_PACKAGE_NAME / SPARQL_PACKAGE_NAME / CONCEPTUAL_MAPPINGS_ASSERTIONS
    metadata_file_path = mapping_suite_package_path / METADATA_FILE_NAME
    resources_folder_path = mapping_suite_package_path / TRANSFORM_PACKAGE_NAME / RESOURCES_PACKAGE_NAME
    mapping_files_resources_folder_path = RESOURCES_PATH / MAPPING_FILES_RESOURCES_FOLDER
    shacl_shape_file_path = RESOURCES_PATH / SHACL_SHAPE_RESOURCES_FOLDER / SHACL_SHAPE_FILE_NAME
    shacl_shape_injection_folder = mapping_suite_package_path / VALIDATE_PACKAGE_NAME / SHACL_PACKAGE_NAME / SHACL_SHAPE_INJECTION_FOLDER
    sparql_queries_resources_folder_path = RESOURCES_PATH / SPARQL_QUERIES_RESOURCES_FOLDER
    sparql_queries_injection_folder = mapping_suite_package_path / VALIDATE_PACKAGE_NAME / SPARQL_PACKAGE_NAME / SPARQL_QUERIES_INJECTION_FOLDER
    shacl_shape_injection_folder.mkdir(parents=True, exist_ok=True)
    cm_sparql_folder_path.mkdir(parents=True, exist_ok=True)
    resources_folder_path.mkdir(parents=True, exist_ok=True)

    mapping_suite_processor_generate_sparql_queries(conceptual_mappings_file_path=conceptual_mappings_file_path,
                                                    output_sparql_queries_folder_path=cm_sparql_folder_path
                                                    )

    mapping_suite_processor_generate_metadata(conceptual_mappings_file_path=conceptual_mappings_file_path,
                                              output_metadata_file_path=metadata_file_path
                                              )

    mapping_suite_processor_inject_resources(conceptual_mappings_file_path=conceptual_mappings_file_path,
                                             resources_folder_path=mapping_files_resources_folder_path,
                                             output_resources_folder_path=resources_folder_path
                                             )

    mapping_suite_processor_inject_shacl_shapes(shacl_shape_file_path=shacl_shape_file_path,
                                                output_shacl_shape_folder_path=shacl_shape_injection_folder
                                                )
    mapping_suite_processor_inject_sparql_queries(sparql_queries_folder_path=sparql_queries_resources_folder_path,
                                                  output_sparql_queries_folder_path=sparql_queries_injection_folder
                                                  )

    mapping_suite_processor_zip_package(mapping_suite_package_path=mapping_suite_package_path)
    mapping_suite_processor_zip_package(mapping_suite_package_path=mapping_suite_package_path, prod_version=True)


def mapping_suite_processor_load_package_in_mongo_db(mapping_suite_package_path: pathlib.Path,
                                                     mongodb_client: MongoClient,
                                                     load_test_data: bool = False
                                                     ):
    """
        This feature allows you to upload a mapping suite package to MongoDB.
    :param mapping_suite_package_path:
    :param mongodb_client:
    :param load_test_data:
    :return:
    """
    mapping_suite_repository_path = mapping_suite_package_path.parent
    mapping_suite_package_name = mapping_suite_package_path.name
    mapping_suite_repository_in_file_system = MappingSuiteRepositoryInFileSystem(
        repository_path=mapping_suite_repository_path)
    mapping_suite_in_memory = mapping_suite_repository_in_file_system.get(reference=mapping_suite_package_name)
    if load_test_data:
        tests_data = mapping_suite_in_memory.transformation_test_data.test_data
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        for test_data in tests_data:
            notice_repository.add(notice=Notice(ted_id=test_data.file_name.split(".")[0],
                                                xml_manifestation=XMLManifestation(object_data=test_data.file_content)))

    mapping_suite_repository_mongo_db = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_suite_repository_mongo_db.add(mapping_suite=mapping_suite_in_memory)


def mapping_suite_processor_from_github_expand_and_load_package_in_mongo_db(mapping_suite_package_name: str,
                                                                            mongodb_client: MongoClient,
                                                                            load_test_data: bool = False
                                                                            ):
    """
        This feature is intended to download a mapping_suite_package from GitHub and process it for upload to MongoDB.
    :param mapping_suite_package_name:
    :param mongodb_client:
    :param load_test_data:
    :return:
    """
    mapping_suite_package_downloader = GitHubMappingSuitePackageDownloader(
        github_repository_url=config.GITHUB_TED_SWS_ARTEFACTS_URL)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir_path = pathlib.Path(tmp_dir)
        mapping_suite_package_downloader.download(mapping_suite_package_name=mapping_suite_package_name,
                                                  output_mapping_suite_package_path=tmp_dir_path)
        mapping_suite_package_path = tmp_dir_path / mapping_suite_package_name
        mapping_suite_processor_expand_package(mapping_suite_package_path=mapping_suite_package_path)
        mapping_suite_processor_load_package_in_mongo_db(mapping_suite_package_path=mapping_suite_package_path,
                                                         mongodb_client=mongodb_client,
                                                         load_test_data=load_test_data
                                                         )
