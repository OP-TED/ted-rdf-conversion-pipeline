from datetime import datetime, time
from typing import Optional, Iterator

from pymongo import MongoClient, ASCENDING

from ted_sws import config
from ted_sws.core.model.supra_notice import DailySupraNotice
from ted_sws.data_manager.adapters.repository_abc import DailySupraNoticeRepositoryABC

DAILY_SUPRA_NOTICE_ID = "notice_fetched_date"


class DailySupraNoticeRepository(DailySupraNoticeRepositoryABC):
    """
       This repository is intended for storing DailySupraNotice objects.
    """

    _collection_name = "daily_supra_notice_collection"
    _database_name = config.MONGO_DB_AGGREGATES_DATABASE_NAME or "aggregates_db"

    def __init__(self, mongodb_client: MongoClient, database_name: str = _database_name):
        self._database_name = database_name
        self.mongodb_client = mongodb_client
        daily_supra_notice_db = mongodb_client[self._database_name]
        self.collection = daily_supra_notice_db[self._collection_name]
        self.collection.create_index([(DAILY_SUPRA_NOTICE_ID, ASCENDING)])

    def _update_daily_supra_notice(self, daily_supra_notice: DailySupraNotice, upsert: bool = False):
        daily_supra_notice_dict = daily_supra_notice.dict()
        daily_supra_notice_dict[DAILY_SUPRA_NOTICE_ID] = datetime.combine(
            daily_supra_notice_dict[DAILY_SUPRA_NOTICE_ID], time())
        self.collection.update_one({DAILY_SUPRA_NOTICE_ID: daily_supra_notice_dict[DAILY_SUPRA_NOTICE_ID]},
                                   {"$set": daily_supra_notice_dict}, upsert=upsert)

    def add(self, daily_supra_notice: DailySupraNotice):
        """
            This method allows you to add daily_supra_notice objects to the repository.
        :param daily_supra_notice:
        :return:
        """
        self._update_daily_supra_notice(daily_supra_notice=daily_supra_notice, upsert=True)

    def update(self, daily_supra_notice: DailySupraNotice):
        """
            This method allows you to update daily_supra_notice objects to the repository
        :param daily_supra_notice:
        :return:
        """
        self._update_daily_supra_notice(daily_supra_notice=daily_supra_notice)

    def get(self, reference) -> Optional[DailySupraNotice]:
        """
            This method allows a daily_supra_notice to be obtained based on an identification reference.
        :param reference:
        :return: DailySupraNotice
        """
        reference = datetime.combine(reference, time())
        result_dict = self.collection.find_one({DAILY_SUPRA_NOTICE_ID: reference})
        if result_dict is not None:
            result_dict[DAILY_SUPRA_NOTICE_ID] = result_dict[DAILY_SUPRA_NOTICE_ID].date()
            daily_supra_notice = DailySupraNotice.parse_obj(result_dict)
            return daily_supra_notice
        return None

    def list(self) -> Iterator[DailySupraNotice]:
        """
            This method allows all records to be retrieved from the repository.
        :return: list of daily_supra_notices
        """
        for result_dict in self.collection.find():
            yield DailySupraNotice(**result_dict)
