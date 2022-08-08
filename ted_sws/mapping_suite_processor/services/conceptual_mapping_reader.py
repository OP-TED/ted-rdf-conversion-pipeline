import pathlib
import tempfile

import pandas as pd
import numpy as np
from pymongo import MongoClient

from ted_sws import config
from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.core.model.notice import Notice
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem, \
    MappingSuiteRepositoryMongoDB
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.mapping_suite_processor import CONCEPTUAL_MAPPINGS_METADATA_SHEET_NAME, \
    CONCEPTUAL_MAPPINGS_RULES_SHEET_NAME, RULES_FIELD_XPATH, RULES_E_FORM_BT_NAME
from ted_sws.mapping_suite_processor.adapters.github_package_downloader import GitHubMappingSuitePackageDownloader
from ted_sws.notice_validator import BASE_XPATH_FIELD
from ted_sws.core.model.transform import ConceptualMapping, ConceptualMappingXPATH

from typing import Dict

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


def mapping_suite_processor_load_package_in_mongo_db(mapping_suite_package_path: pathlib.Path,
                                                     mongodb_client: MongoClient,
                                                     load_test_data: bool = False,
                                                     git_last_commit_hash: str = None
                                                     ):
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

    if git_last_commit_hash is not None:
        mapping_suite_in_memory.git_latest_commit_hash = git_last_commit_hash

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
    default_github_repository_url = "https://github.com/meaningfy-ws/ted-sws-artefacts.git"
    mapping_suite_package_downloader = GitHubMappingSuitePackageDownloader(
        github_repository_url=config.GITHUB_TED_SWS_ARTEFACTS_URL or default_github_repository_url)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir_path = pathlib.Path(tmp_dir)
        git_last_commit_hash = mapping_suite_package_downloader.download(
            mapping_suite_package_name=mapping_suite_package_name,
            output_mapping_suite_package_path=tmp_dir_path)
        mapping_suite_package_path = tmp_dir_path / mapping_suite_package_name
        mapping_suite_processor_load_package_in_mongo_db(mapping_suite_package_path=mapping_suite_package_path,
                                                         mongodb_client=mongodb_client,
                                                         load_test_data=load_test_data,
                                                         git_last_commit_hash=git_last_commit_hash
                                                         )


def mapping_suite_read_metadata(conceptual_mappings_file_path: pathlib.Path) -> Dict:
    """
        This feature allows you to read the conceptual mapping metadata.
    :param conceptual_mappings_file_path:
    :return:
    """

    metadata = {}
    with open(conceptual_mappings_file_path, 'rb') as excel_file:
        metadata_df = pd.read_excel(excel_file, sheet_name=CONCEPTUAL_MAPPINGS_METADATA_SHEET_NAME)
        metadata = metadata_df.set_index('Field').T.to_dict('list')
        base_xpath = metadata[BASE_XPATH_FIELD][0]
        print("K :: ", metadata)

    return metadata


def mapping_suite_read_conceptual_mapping(conceptual_mappings_file_path: pathlib.Path,
                                          metadata: Dict = None) -> ConceptualMapping:
    """
        This feature allows you to read the c1onceptual mapping in a package.
    :param conceptual_mappings_file_path:
    :param metadata:
    :return:
    """

    if metadata is None:
        metadata = mapping_suite_read_metadata(conceptual_mappings_file_path)
    conceptual_mapping = ConceptualMapping()
    conceptual_mapping_xpaths = []
    with open(conceptual_mappings_file_path, 'rb') as excel_file:
        base_xpath = metadata[BASE_XPATH_FIELD][0]
        rules_df = pd.read_excel(excel_file, sheet_name=CONCEPTUAL_MAPPINGS_RULES_SHEET_NAME, header=1)
        df_xpaths = rules_df[RULES_FIELD_XPATH].tolist()
        df_bt_names = rules_df[RULES_E_FORM_BT_NAME].tolist()
        processed_xpaths = set()
        for idx, xpath_row in enumerate(df_xpaths):
            if xpath_row is not np.nan:
                row_xpaths = xpath_row.split('\n')
                for xpath in row_xpaths:
                    if xpath:
                        xpath = base_xpath + "/" + xpath
                        if xpath not in processed_xpaths:
                            xpath_name = df_bt_names[idx]
                            cm_xpath = ConceptualMappingXPATH(xpath=xpath, name=xpath_name)
                            conceptual_mapping_xpaths.append(cm_xpath)
                            processed_xpaths.add(xpath)

    conceptual_mapping.xpaths = conceptual_mapping_xpaths

    return conceptual_mapping
