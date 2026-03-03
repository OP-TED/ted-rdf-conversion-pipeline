from pathlib import Path

import pandas as pd
from pymongo import MongoClient

from src.ted_sws import config
from src.ted_sws.core.model.notice import Notice
from src.ted_sws.data_manager.adapters.mapping_package_repository import MappingPackageRepositoryMongoDB
from src.ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryMongoDB

COUNTRIES_MAPPING_FILE = "country.json"
FORM_TYPE_MAPPING_FILE = "form_type.json"
LANGUAGES_MAPPING_FILE = "languages.json"
LEGAL_BASIS_MAPPING_FILE = "legal_basis.json"
NOTICE_TYPE_MAPPING_FILE = "notice_type.json"
NUTS_CODES_MAPPING_FILE = "nuts.json"
STANDARD_FORMS_MAPPING_FILE = "sforms_mapping.csv"
E_FORMS_FORMS_MAPPING_FILE = "eforms_mapping.csv"
FILTER_MAPPING_FILE = "df_filter_map.csv"

CSV_EXT = ".csv"


class MappingFilesRegistry:
    """
     Registry of mapping files. This will return the specific file content
    """

    def __init__(self, notice: Notice, mongodb_client: MongoClient = None):
        if not mongodb_client:
            mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        mapping_package_repository = MappingPackageRepositoryMongoDB(mongodb_client=mongodb_client)
        mapping_package = mapping_package_repository.get(notice.mapping_package_identifier)
        mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
        self.mapping_suite = mapping_suite_repository.get(mapping_package.mapping_suite_identifier)

    @staticmethod
    def extract_filename_from_path(path: str) -> str:
        return Path(path).name if path else None

    @staticmethod
    def extract_filename_ext(path: str) -> str:
        return Path(path).suffix if path else None

    def get_suite_resource_content(self, filename: str):
        resources = self.mapping_suite.resource_file_contents or []
        resource = next(
            (
                r for r in resources
                if self.extract_filename_from_path(r['file_name']) == filename
            ),
            None
        )

        resource_content = resource['object'] if resource else None

        if self.extract_filename_ext(filename) == CSV_EXT:
            return pd.DataFrame(resource_content).apply(pd.to_numeric, errors="ignore").fillna("")

        return resource_content

    @property
    def countries(self):
        return self.get_suite_resource_content(COUNTRIES_MAPPING_FILE)

    @property
    def form_type(self):
        return self.get_suite_resource_content(FORM_TYPE_MAPPING_FILE)

    @property
    def languages(self):
        return self.get_suite_resource_content(LANGUAGES_MAPPING_FILE)

    @property
    def legal_basis(self):
        return self.get_suite_resource_content(LEGAL_BASIS_MAPPING_FILE)

    @property
    def notice_type(self):
        return self.get_suite_resource_content(NOTICE_TYPE_MAPPING_FILE)

    @property
    def nuts(self):
        return self.get_suite_resource_content(NUTS_CODES_MAPPING_FILE)

    @property
    def sf_notice_df(self):
        return self.get_suite_resource_content(STANDARD_FORMS_MAPPING_FILE)

    @property
    def ef_notice_df(self):
        return self.get_suite_resource_content(E_FORMS_FORMS_MAPPING_FILE)

    @property
    def filter_map_df(self):
        return self.get_suite_resource_content(FILTER_MAPPING_FILE)
