from pymongo import MongoClient

from src.ted_sws import config
from src.ted_sws.core.model.notice import Notice
from src.ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryMongoDB
from src.ted_sws.resources.mapping_files_registry import MappingSuiteConfigError


class NoticeProber:
    def __init__(self, notice: Notice, mongodb_client: MongoClient = None):
        self.notice = notice
        if not mongodb_client:
            mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        self.mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)

    def get_mapping_suite(self):
        mapping_suites = self.mapping_suite_repository.list()
        if not mapping_suites:
            raise MappingSuiteConfigError(
                "No MappingSuite found in the database. Please ensure at least one "
                "mapping suite is loaded before attempting the notice probing."
            )
        for mapping_suite in mapping_suites:
            if self.probe_notice(mapping_suite):
