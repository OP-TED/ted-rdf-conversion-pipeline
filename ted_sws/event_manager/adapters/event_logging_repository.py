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
    _collection_name = "log_events"

    def __init__(self, mongodb_client: MongoClient = None, database_name: str = _database_name,
                 collection_name: str = _collection_name):
        self._database_name = database_name
        self._collection_name = collection_name
        if mongodb_client is None:
            mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        self.mongodb_client = mongodb_client
        events_db = mongodb_client[self._database_name]
        if self._collection_name:
            self.collection = events_db[self._collection_name]
            self.create_indexes()
        else:
            raise ValueError("No collection provided!")

    def create_indexes(self):
        self.collection.create_index([("year", DESCENDING)])
        self.collection.create_index([("month", ASCENDING)])
        self.collection.create_index([("day", ASCENDING)])

    @classmethod
    def prepare_record(cls, event_message: EventMessage) -> dict:
        return event_message.dict()

    def get_database_name(self) -> str:
        return self._database_name

    def get_collection_name(self) -> str:
        return self._collection_name

    def add(self, event_message: EventMessage) -> str:
        record = self.prepare_record(event_message)
        result = self.collection.insert_one(record)
        return result.inserted_id


class TechnicalEventRepository(EventLoggingRepository):
    _database_name = EventLoggingRepository._database_name
    _collection_name = "technical_events"

    def __init__(self, mongodb_client: MongoClient, database_name: str = _database_name,
                 collection_name: str = _collection_name):
        super().__init__(mongodb_client, database_name, collection_name)


class NoticeEventRepository(EventLoggingRepository):
    _database_name = EventLoggingRepository._database_name
    _collection_name = "notice_events"

    def __init__(self, mongodb_client: MongoClient, database_name: str = _database_name,
                 collection_name: str = _collection_name):
        super().__init__(mongodb_client, database_name, collection_name)


class MappingSuiteEventRepository(EventLoggingRepository):
    _database_name = EventLoggingRepository._database_name
    _collection_name = "mapping_suite_events"

    def __init__(self, mongodb_client: MongoClient, database_name: str = _database_name,
                 collection_name: str = _collection_name):
        super().__init__(mongodb_client, database_name, collection_name)
