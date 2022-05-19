from datetime import datetime

from dateutil import rrule

from dags import DEFAULT_DAG_ARGUMENTS
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from pymongo import MongoClient

from ted_sws import config
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_sampler.services.notice_xml_indexer import index_notice
from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, TedRequestAPI
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher

START_DATE_KEY = "start_date"
END_DATE_KEY = "end_date"


def generate_daily_dates(start_date: str, end_date: str) -> list:
    """
        Given a date range returns all daily dates in that range
    :param start_date:
    :param end_date:
    :return:
    """
    return [dt.strftime('%Y%m%d')
            for dt in rrule.rrule(rrule.DAILY,
                                  dtstart=datetime.strptime(start_date, '%Y%m%d'),
                                  until=datetime.strptime(end_date, '%Y%m%d'))]


def generate_wild_card_by_date(date: str) -> str:
    """
        Method to build a wildcard_date from a date string
    :param date:
    :return:
    """
    return f"{date}*"


@dag(default_args=DEFAULT_DAG_ARGUMENTS, tags=['selector', 'daily-fetch'])
def selector_notice_fetch_orchestrator():
    @task
    def fetch_notice_from_ted():
        context = get_current_context()
        dag_conf = context["dag_run"].conf

        if START_DATE_KEY not in dag_conf.keys():
            raise "Config key [start_date] is not present in dag context"
        if END_DATE_KEY not in dag_conf.keys():
            raise "Config key [end_date] is not present in dag context"

        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        for generated_date in generate_daily_dates(dag_conf[START_DATE_KEY], dag_conf[END_DATE_KEY]):
            NoticeFetcher(notice_repository=NoticeRepository(mongodb_client=mongodb_client),
                          ted_api_adapter=TedAPIAdapter(request_api=TedRequestAPI())).fetch_notices_by_date_wild_card(
                wildcard_date=generate_wild_card_by_date(date=generated_date))  # "20220203*"

    @task
    def index_notices():
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        notices = notice_repository.get_notice_by_status(notice_status=NoticeStatus.RAW)
        for notice in notices:
            indexed_notice = index_notice(notice=notice)
            notice_repository.update(notice=indexed_notice)

    fetch_notice_from_ted() >> index_notices()


dag = selector_notice_fetch_orchestrator()
