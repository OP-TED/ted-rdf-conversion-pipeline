from typing import List
from pymongo import MongoClient
from ted_sws.domain.adapters.repository_abc import NoticeRepositoryABC
from ted_sws.domain.model.notice import Notice


class NoticeRepository(NoticeRepositoryABC):

    _collection_name = "notice_collection"
    _database_name = "notice_db"


    def __init__(self,mongodb_client: MongoClient):
        mongodb_client = mongodb_client
        notice_db = mongodb_client[self._database_name]
        self.collection = notice_db[self._collection_name]

    def add(self, notice: Notice):
        notice_dict = notice.dict()
        notice_dict["_id"] = notice_dict["ted_id"]
        self.collection.insert_one(notice_dict)

    def get(self, reference) -> Notice:
        pass

    def list(self) -> List[str]:
        pass