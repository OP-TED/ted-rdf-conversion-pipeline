from datetime import datetime, time
from typing import Optional, Iterator

from pymongo import MongoClient, ASCENDING

from ted_sws import config
from ted_sws.core.model.supra_notice import DailySupraNotice
from ted_sws.data_manager.adapters import inject_date_string_fields, remove_date_string_fields
from ted_sws.data_manager.adapters.repository_abc import DailySupraNoticeRepositoryABC

DAILY_SUPRA_NOTICE_FETCHED_DATE = "notice_fetched_date"
DAILY_SUPRA_NOTICE_CREATED_AT = "created_at"
DAILY_SUPRA_NOTICE_ID = "_id"


class DailySupraNoticeRepository(DailySupraNoticeRepositoryABC):
    """
       This repository is intended for storing DailySupraNotice objects.
    """

    _collection_name = "daily_supra_notice_collection"

    def __init__(self, mongodb_client: MongoClient, database_name: str = None):
        self._database_name = database_name or config.MONGO_DB_AGGREGATES_DATABASE_NAME
        self.mongodb_client = mongodb_client
        daily_supra_notice_db = mongodb_client[self._database_name]
        self.collection = daily_supra_notice_db[self._collection_name]
        self.collection.create_index(
            [(DAILY_SUPRA_NOTICE_FETCHED_DATE, ASCENDING)])  # TODO: index creation may bring race condition error.

    def _create_dict_from_daily_supra_notice(self, daily_supra_notice: DailySupraNotice) -> dict:
        """

        :param daily_supra_notice:
        :return:
        """
        daily_supra_notice_dict = daily_supra_notice.dict()
        daily_supra_notice_dict[DAILY_SUPRA_NOTICE_FETCHED_DATE] = datetime.combine(
            daily_supra_notice_dict[DAILY_SUPRA_NOTICE_FETCHED_DATE], time())
        daily_supra_notice_dict[DAILY_SUPRA_NOTICE_ID] = daily_supra_notice_dict[DAILY_SUPRA_NOTICE_FETCHED_DATE].isoformat()
        inject_date_string_fields(data=daily_supra_notice_dict, date_field_name=DAILY_SUPRA_NOTICE_FETCHED_DATE)
        inject_date_string_fields(data=daily_supra_notice_dict, date_field_name=DAILY_SUPRA_NOTICE_CREATED_AT)
        return daily_supra_notice_dict

    def _create_daily_supra_notice_from_dict(self, daily_supra_notice_dict: dict) -> Optional[DailySupraNotice]:
        """

        :param daily_supra_notice_dict:
        :return:
        """
        if daily_supra_notice_dict is not None:
            daily_supra_notice_dict.pop(DAILY_SUPRA_NOTICE_ID, None)
            daily_supra_notice_dict[DAILY_SUPRA_NOTICE_FETCHED_DATE] = daily_supra_notice_dict[
                DAILY_SUPRA_NOTICE_FETCHED_DATE].date()
            remove_date_string_fields(data=daily_supra_notice_dict, date_field_name=DAILY_SUPRA_NOTICE_FETCHED_DATE)
            remove_date_string_fields(data=daily_supra_notice_dict, date_field_name=DAILY_SUPRA_NOTICE_CREATED_AT)
            daily_supra_notice = DailySupraNotice.parse_obj(daily_supra_notice_dict)
            return daily_supra_notice
        return None

    def _update_daily_supra_notice(self, daily_supra_notice: DailySupraNotice, upsert: bool = False):
        daily_supra_notice_dict = self._create_dict_from_daily_supra_notice(daily_supra_notice=daily_supra_notice)
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
        reference = datetime.combine(reference, time()).isoformat()
        result_dict = self.collection.find_one({DAILY_SUPRA_NOTICE_ID: reference})
        return self._create_daily_supra_notice_from_dict(daily_supra_notice_dict=result_dict)

    def list(self) -> Iterator[DailySupraNotice]:
        """
            This method allows all records to be retrieved from the repository.
        :return: list of daily_supra_notices
        """
        for result_dict in self.collection.find():
            yield self._create_daily_supra_notice_from_dict(daily_supra_notice_dict=result_dict)
