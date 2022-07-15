import abc

from pymongo import MongoClient, ASCENDING, DESCENDING

from ted_sws import config
from ted_sws.event_manager.model.event_message import EventMessage


"""
This module contains the event logging repository adapters.
"""


class EventLoggingRepositoryABC(abc.ABC):
    """
    This repository is intended for storing event logs.
    """

    @abc.abstractmethod
    def add(self, event_message: EventMessage) -> str:
        """
        This method allows you to add event messages to the repository.

        :param event_message: The event message to be added to the repository
        :return: The result string
        """


class EventLoggingRepository(EventLoggingRepositoryABC):
    """
    This is the base/generic events' repository class.
    """
    _database_name = config.MONGO_DB_LOGS_DATABASE_NAME or "logs_db"
    _collection_name = "log_events"

    def __init__(self, mongodb_client: MongoClient = None, database_name: str = _database_name,
                 collection_name: str = _collection_name):
        """
        This is the constructor/initialization of base/generic event logging repository.

        :param mongodb_client: The MongoDB client
        :param database_name: The database name
        :param collection_name: The collection name
        """
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
        """
        This method ensures that collection indexes are set.

        :return: None
        """
        self.collection.create_index([("year", DESCENDING)])
        self.collection.create_index([("month", ASCENDING)])
        self.collection.create_index([("day", ASCENDING)])

    @classmethod
    def prepare_record(cls, event_message: EventMessage) -> dict:
        """
        This method prepares the event message to be added to event repository.

        :param event_message: The event message
        :return: The event message dict
        """
        return event_message.dict()

    def get_database_name(self) -> str:
        """
        This method returns the database name.

        :return: The database name
        """
        return self._database_name

    def get_collection_name(self) -> str:
        """
        This method returns the collection name.

        :return: The collection name
        """
        return self._collection_name

    def add(self, event_message: EventMessage) -> str:
        """
        This method adds the event message to event repository.

        :param event_message: The event message to be added
        :return:
        """
        record = self.prepare_record(event_message)
        result = self.collection.insert_one(record)
        return result.inserted_id

    @classmethod
    def get_default_database_name(cls):
        return cls._database_name


class TechnicalEventRepository(EventLoggingRepository):
    """
    This is the technical events' repository class.
    """
    _database_name = EventLoggingRepository._database_name
    _collection_name = "technical_events"

    def __init__(self, mongodb_client: MongoClient, database_name: str = _database_name,
                 collection_name: str = _collection_name):
        """
        This is the constructor/initialization of technical event logging repository.

        :param mongodb_client: The MongoDB client
        :param database_name: The database name
        :param collection_name: The collection name
        """
        super().__init__(mongodb_client, database_name, collection_name)


class NoticeEventRepository(EventLoggingRepository):
    """
    This is the notice events' repository class.
    """
    _database_name = EventLoggingRepository._database_name
    _collection_name = "notice_events"

    def __init__(self, mongodb_client: MongoClient, database_name: str = _database_name,
                 collection_name: str = _collection_name):
        """
        This is the constructor/initialization of notice event logging repository.

        :param mongodb_client: The MongoDB client
        :param database_name: The database name
        :param collection_name: The collection name
        """
        super().__init__(mongodb_client, database_name, collection_name)


class MappingSuiteEventRepository(EventLoggingRepository):
    """
    This is the mapping suite events' repository class.
    """
    _database_name = EventLoggingRepository._database_name
    _collection_name = "mapping_suite_events"

    def __init__(self, mongodb_client: MongoClient, database_name: str = _database_name,
                 collection_name: str = _collection_name):
        """
        This is the constructor/initialization of mapping suite event logging repository.

        :param mongodb_client: The MongoDB client
        :param database_name: The database name
        :param collection_name: The collection name
        """
        super().__init__(mongodb_client, database_name, collection_name)
