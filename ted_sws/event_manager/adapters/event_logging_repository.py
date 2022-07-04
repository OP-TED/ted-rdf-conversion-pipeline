import abc

from pymongo import MongoClient, ASCENDING, DESCENDING

from ted_sws import config
from ted_sws.event_manager.model.event_message import EventMessage


class EventLoggingRepositoryABC(abc.ABC):
    """
       This repository is intended for storing Event logs.
    """

    @abc.abstractmethod
    def add(self, event_message: EventMessage):
        """
            This method allows you to add Event Messages to the repository.
        :param event_message:
        :return:
        """


class EventLoggingRepository(EventLoggingRepositoryABC):
    _database_name = config.MONGO_DB_LOGS_DATABASE_NAME
    _collection_name = None

    def __init__(self, mongodb_client: MongoClient, database_name: str = _database_name):
        self._database_name = database_name
        self.mongodb_client = mongodb_client
        event_db = mongodb_client[self._database_name]
        if self._collection_name is not None:
            self.collection = event_db[self._collection_name]
            self.create_indexes()
        else:
            raise Exception("No collection provided!")

    def create_indexes(self):
        self.collection.create_index([("year", DESCENDING)])
        self.collection.create_index([("month", ASCENDING)])
        self.collection.create_index([("day", ASCENDING)])

    @classmethod
    def _prepare_record(cls, event_message: EventMessage) -> dict:
        return event_message.dict()

    def add(self, event_message: EventMessage) -> str:
        record = self._prepare_record(event_message)
        result = self.collection.insert_one(record)
        return result.inserted_id


class TechnicalEventRepository(EventLoggingRepository):
    _collection_name = "technical_events"


class NoticeEventRepository(EventLoggingRepository):
    _collection_name = "notice_events"


class MappingSuiteEventRepository(EventLoggingRepository):
    _collection_name = "mapping_suite_events"

