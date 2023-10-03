from datetime import datetime, time, date
from typing import Iterator, Optional, List

from pymongo import MongoClient, ASCENDING

from ted_sws import config
from ted_sws.core.model.supra_notice import DailyNoticesMetadata
from ted_sws.data_manager.adapters import inject_date_string_fields
from ted_sws.data_manager.adapters.repository_abc import DailyNoticesMetadataRepositoryABC

DAILY_NOTICES_METADATA_AGGREGATION_DATE = "aggregation_date"
DAILY_NOTICES_METADATA_ID = "_id"


class DailyNoticesMetadataRepository(DailyNoticesMetadataRepositoryABC):
    """
       This repository is intended for storing DailyNoticesMetadata objects.
    """

    _collection_name = "daily_notices_metadata_collection"

    def __init__(self, mongodb_client: MongoClient, database_name: str = None):
        self._database_name = database_name or config.MONGO_DB_AGGREGATES_DATABASE_NAME
        self.mongodb_client = mongodb_client
        daily_supra_notice_db = mongodb_client[self._database_name]
        self.collection = daily_supra_notice_db[self._collection_name]
        self.collection.create_index(
            [(DAILY_NOTICES_METADATA_AGGREGATION_DATE,
              ASCENDING)])  # TODO: index creation may bring race condition error.

    def _update_daily_notices_metadata(self, daily_notices_metadata: DailyNoticesMetadata, upsert: bool = False):
        """
            Updates a DailyNoticesMetadata object in the repository.
        :param daily_notices_metadata:
        :param upsert:
        :return:
        """
        daily_notices_metadata_dict = daily_notices_metadata.model_dump()
        daily_notices_metadata_dict[DAILY_NOTICES_METADATA_AGGREGATION_DATE] = daily_notices_metadata_dict[
            DAILY_NOTICES_METADATA_AGGREGATION_DATE].isoformat()
        self.collection.update_one(
            {DAILY_NOTICES_METADATA_ID: daily_notices_metadata_dict[DAILY_NOTICES_METADATA_AGGREGATION_DATE]},
            {"$set": daily_notices_metadata_dict}, upsert=upsert)

    def _create_daily_notices_metadata_from_dict(self, daily_notices_metadata_dict: dict) -> Optional[
        DailyNoticesMetadata]:
        """
            Creates a DailyNoticesMetadata object from a dictionary.
        :param daily_notices_metadata_dict:
        :return:
        """
        if not daily_notices_metadata_dict:
            return None
        daily_notices_metadata_dict[DAILY_NOTICES_METADATA_AGGREGATION_DATE] = datetime.fromisoformat(
            daily_notices_metadata_dict[
                DAILY_NOTICES_METADATA_AGGREGATION_DATE])
        daily_notices_metadata_dict.pop(DAILY_NOTICES_METADATA_ID, None)
        return DailyNoticesMetadata.model_validate(daily_notices_metadata_dict)

    def add(self, daily_notices_metadata: DailyNoticesMetadata):
        """
            Adds a DailyNoticesMetadata object to the repository.
        :param daily_notices_metadata:
        :return:
        """
        self._update_daily_notices_metadata(daily_notices_metadata=daily_notices_metadata, upsert=True)

    def update(self, daily_notices_metadata: DailyNoticesMetadata):
        """
            Updates a DailyNoticesMetadata object in the repository.
        :param daily_notices_metadata:
        :return:
        """
        self._update_daily_notices_metadata(daily_notices_metadata=daily_notices_metadata)

    def get(self, reference) -> DailyNoticesMetadata:
        """
            Gets a DailyNoticesMetadata object from the repository.
        :param reference:
        :return:
        """
        reference = reference.isoformat()
        result_dict = self.collection.find_one({DAILY_NOTICES_METADATA_ID: reference})
        return self._create_daily_notices_metadata_from_dict(daily_notices_metadata_dict=result_dict)

    def list(self) -> Iterator[DailyNoticesMetadata]:
        """
            Gets all DailyNoticesMetadata objects from the repository.
        :return:
        """
        for result_dict in self.collection.find():
            yield self._create_daily_notices_metadata_from_dict(daily_notices_metadata_dict=result_dict)

    def list_daily_notices_metadata_aggregation_date(self) -> List[date]:
        """
            Gets all DailyNoticesMetadata ids from the repository.
        :return:
        """
        daily_notices_metadata_list = list(self.collection.find({},
                                                                {DAILY_NOTICES_METADATA_AGGREGATION_DATE: 1,
                                                                 DAILY_NOTICES_METADATA_ID: 0}))
        if not daily_notices_metadata_list:
            return []
        return [datetime.fromisoformat(aggregation_date[DAILY_NOTICES_METADATA_AGGREGATION_DATE]) for aggregation_date
                in daily_notices_metadata_list]
