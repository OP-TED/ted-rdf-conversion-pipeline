from pymongo import MongoClient, ASCENDING, DESCENDING

from ted_sws import config
from ted_sws.event_manager.model.message import DBProcessLog as Log
from typing import Union
from bson import ObjectId

MONGODB_COLLECTION_ID = "_id"


class LogRepository:
    """
       This repository is intended for storing Log objects.
    """

    collection = None
    _instance = None

    _collection_name = "logs"
    _database_name = config.MONGO_DB_LOGS_DATABASE_NAME

    def __new__(cls, mongodb_client: MongoClient = None, database_name: str = _database_name):
        if cls._instance is None:
            if mongodb_client is None:
                mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
            cls._database_name = database_name
            cls.mongodb_client = mongodb_client
            log_db = mongodb_client[cls._database_name]

            cls.collection = log_db[cls._collection_name]
            cls.collection.create_index([("year", DESCENDING)])
            cls.collection.create_index([("month", ASCENDING)])
            cls.collection.create_index([("day", ASCENDING)])

            cls._instance = super(LogRepository, cls).__new__(cls)

        return cls._instance

    def get_database_name(self):
        return self._database_name

    @staticmethod
    def create_dict_from_log(log: Log) -> dict:
        """
        """

        log_dict = log.dict()

        return log_dict

    @staticmethod
    def create_log_from_dict(log_dict: dict) -> Union[Log, None]:
        """
        """

        del log_dict[MONGODB_COLLECTION_ID]
        log = Log(**log_dict)
        return log

    def add(self, log: Log) -> str:
        """
        """
        log_dict = LogRepository.create_dict_from_log(log=log)
        result = self.collection.insert_one(log_dict)
        return result.inserted_id

    def update(self, _id: str, log: Log) -> str:
        """
        """
        log_dict = LogRepository.create_dict_from_log(log=log)
        self.collection.update_one({"_id": ObjectId(_id)}, {"$set": log_dict}, upsert=True)
        return _id
