import logging
from typing import Iterator
from pymongo import MongoClient

from ted_sws import config
from ted_sws.data_manager.adapters.repository_abc import NoticeRepositoryABC
from ted_sws.core.model.notice import Notice, NoticeStatus

logger = logging.getLogger(__name__)


class NoticeRepository(NoticeRepositoryABC):
    """
       This repository is intended for storing Notice objects.
    """

    _collection_name = "notice_collection"
    _database_name = config.MONGO_DB_AGGREGATES_DATABASE_NAME

    def __init__(self, mongodb_client: MongoClient, database_name: str = _database_name):
        mongodb_client = mongodb_client
        self._database_name = database_name
        notice_db = mongodb_client[self._database_name]
        self.collection = notice_db[self._collection_name]

    def add(self, notice: Notice):
        """
            This method allows you to add notice objects to the repository.
        :param notice:
        :return:
        """
        notice_dict = notice.dict()
        notice_dict["_id"] = notice_dict["ted_id"]
        try:
            self.collection.insert_one(notice_dict)
        except Exception as e:
            logger.warning(f"Failed to add notice with id={notice_dict['ted_id']}, with error message: "+str(e))

    def update(self, notice: Notice):
        """
            This method allows you to update notice objects to the repository
        :param notice:
        :return:
        """
        notice_dict = notice.dict()
        notice_dict["_id"] = notice_dict["ted_id"]
        self.collection.update_one({'_id': notice_dict["_id"]}, {"$set": notice_dict})

    def get(self, reference) -> Notice:
        """
            This method allows a notice to be obtained based on an identification reference.
        :param reference:
        :return: Notice
        """
        result_dict = self.collection.find_one({"ted_id": reference})
        return Notice(**result_dict) if result_dict else None

    def get_notice_by_status(self, notice_status: NoticeStatus) -> Iterator[Notice]:
        """
            This method provides all notices based on its status.
        :param notice_status:
        :return:
        """
        for result_dict in self.collection.find({"status": notice_status}):
            yield Notice(**result_dict)

    def list(self) -> Iterator[Notice]:
        """
            This method allows all records to be retrieved from the repository.
        :return: list of notices
        """
        for result_dict in self.collection.find():
            yield Notice(**result_dict)
