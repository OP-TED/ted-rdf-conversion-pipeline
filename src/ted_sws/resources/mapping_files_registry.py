from pathlib import Path

import pandas as pd
from pymongo import MongoClient

from src.ted_sws import config
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


class MappingSuiteConfigError(Exception):
    """Raised when no MappingSuite is found in the database."""
    pass


class MappingFilesRegistry:
    """
     Registry of mapping files. This will return the specific file content.

     Resource files (country.json, languages.json, etc.) are global and identical
     across all mapping packages, so we can load them from any available MappingSuite.
    """

    def __init__(self, mongodb_client: MongoClient = None):
        if not mongodb_client:
            mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
        # Get any available MappingSuite - resources are global/identical across all suites
        all_suites = mapping_suite_repository.list()
        if not all_suites:
            raise MappingSuiteConfigError(
                "No MappingSuite found in the database. Please ensure at least one "
                "mapping suite is loaded before attempting to normalise notices."
            )
        self.mapping_suite = all_suites[0]

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
