import pathlib
from typing import Iterator

from pymongo import MongoClient

from ted_sws.domain.adapters.repository_abc import MappingSuiteRepositoryABC
from ted_sws.domain.model.transform import MappingSuite


class MappingSuiteRepositoryMongoDB(MappingSuiteRepositoryABC):
    """
       This repository is intended for storing MappingSuite objects in MongoDB.
    """

    _collection_name = "mapping_suite_collection"
    _database_name = "mapping_suite_db"

    def __init__(self, mongodb_client: MongoClient, database_name: str = None):
        """

        :param mongodb_client:
        :param database_name:
        """
        mongodb_client = mongodb_client
        notice_db = mongodb_client[database_name if database_name else self._database_name]
        self.collection = notice_db[self._collection_name]

    def add(self, mapping_suite: MappingSuite):
        """
            This method allows you to add MappingSuite objects to the repository.
        :param mapping_suite:
        :return:
        """
        mapping_suite_dict = mapping_suite.dict()
        mapping_suite_dict["_id"] = mapping_suite_dict["identifier"]
        self.collection.insert_one(mapping_suite_dict)

    def update(self, mapping_suite: MappingSuite):
        """
            This method allows you to update MappingSuite objects to the repository
        :param mapping_suite:
        :return:
        """
        mapping_suite_dict = mapping_suite.dict()
        mapping_suite_dict["_id"] = mapping_suite_dict["identifier"]
        self.collection.update_one({'_id': mapping_suite_dict["_id"]}, {"$set": mapping_suite_dict})

    def get(self, reference) -> MappingSuite:
        """
            This method allows a MappingSuite to be obtained based on an identification reference.
        :param reference:
        :return: MappingSuite
        """
        result_dict = self.collection.find_one({"identifier": reference})
        return MappingSuite(**result_dict) if result_dict else None

    def list(self) -> Iterator[MappingSuite]:
        """
            This method allows all records to be retrieved from the repository.
        :return: list of MappingSuites
        """
        for result_dict in self.collection.find():
            yield MappingSuite(**result_dict)


class MappingSuiteRepositoryInFileSystem(MappingSuiteRepositoryABC):
    """
           This repository is intended for storing MappingSuite objects in FileSystem.
    """

    def __init__(self, repository_path: pathlib.Path):
        pass

    def add(self, mapping_suite: MappingSuite):
        """
            This method allows you to add MappingSuite objects to the repository.
        :param mapping_suite:
        :return:
        """
        pass

    def update(self, mapping_suite: MappingSuite):
        """
            This method allows you to update MappingSuite objects to the repository
        :param mapping_suite:
        :return:
        """
        pass

    def get(self, reference) -> MappingSuite:
        """
            This method allows a MappingSuite to be obtained based on an identification reference.
        :param reference:
        :return: MappingSuite
        """
        pass

    def list(self) -> Iterator[MappingSuite]:
        """
            This method allows all records to be retrieved from the repository.
        :return: list of MappingSuites
        """
        pass
