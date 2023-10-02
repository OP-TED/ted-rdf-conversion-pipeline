from datetime import date, datetime, timedelta
from typing import Optional

from dateutil import rrule
from pymongo import MongoClient

from ted_sws import config
from ted_sws.data_manager.adapters.daily_notices_metadata_repository import DailyNoticesMetadataRepository
from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, TedRequestAPI

DEFAULT_TED_API_START_DATE = "2023-09-01" # TODO: Change to 2014-01-01
DEFAULT_TED_API_START_DATE_FORMAT = "%Y-%m-%d"


def generate_list_of_dates_from_date_range(start_date: date, end_date: date) -> Optional[list]:
    """
        Given a date range returns all daily dates in that range
    :param start_date:
    :param end_date:
    :return:
    """
    if start_date > end_date:
        return None
    return [dt for dt in rrule.rrule(rrule.DAILY,
                                     dtstart=start_date,
                                     until=end_date)]


def update_daily_notices_metadata_from_ted(start_date: date = None,
                                           end_date: date = None,
                                           ted_api: TedAPIAdapter = None,
                                           mongo_client: MongoClient = None,
                                           daily_notices_metadata_repo: DailyNoticesMetadataRepository = None):
    """
    Updates the daily notices metadata from the TED API.
    """
    start_date = start_date or datetime.strptime(DEFAULT_TED_API_START_DATE, DEFAULT_TED_API_START_DATE_FORMAT)
    end_date = end_date or datetime.today() - timedelta(days=1)

    if start_date > end_date:
        raise Exception("Start date cannot be greater than end date")

    ted_api = ted_api or TedAPIAdapter(TedRequestAPI(), config.TED_API_URL)
    mongo_client = mongo_client or MongoClient(config.MONGO_DB_AUTH_URL)
    daily_notices_metadata_repo = daily_notices_metadata_repo or DailyNoticesMetadataRepository(mongo_client)

    # Generate list of dates from date range
    date_range = generate_list_of_dates_from_date_range(start_date, end_date)

    # Getting from metadata repository dates that are not in the repository from date range
    dates_not_in_repository = [day for day in date_range if not daily_notices_metadata_repo.get(day)] # TODO: Lazy evaluation

    # Getting from TED API dates that are not in the repository from date range
    #ted_api.get_by_query(query={"q": ""})

