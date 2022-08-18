from typing import List

from pymongo import MongoClient
from datetime import date, datetime, time
from ted_sws.core.model.supra_notice import DailySupraNotice
from ted_sws.data_manager.adapters.supra_notice_repository import DailySupraNoticeRepository


def create_and_store_in_mongo_db_daily_supra_notice(notice_ids: List[str], mongodb_client: MongoClient,
                                                    notice_publication_date: date = date.today()):
    """
        This function creates and stores a DailySupraNotice in MongoDB.
    :param notice_ids:
    :param mongodb_client:
    :param notice_publication_date:
    :return:
    """
    daily_supra_notice_repository = DailySupraNoticeRepository(mongodb_client=mongodb_client)
    daily_supra_notice = DailySupraNotice(notice_publication_date=notice_publication_date,
                                          notice_ids=notice_ids)
    daily_supra_notice_repository.add(daily_supra_notice=daily_supra_notice)
