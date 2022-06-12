from dags import DEFAULT_DAG_ARGUMENTS
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from pymongo import MongoClient

from ted_sws import config
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_sampler.services.notice_xml_indexer import index_notice
from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, TedRequestAPI
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher
from ted_sws.core.model.notice import NoticeStatus
import datetime


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     catchup=False,
     schedule_interval="0 3 * * *",
     tags=['selector', 'daily-fetch'])
def selector_daily_fetch_orchestrator():
    @task
    def fetch_notice_from_ted():
        current_datetime_wildcard = (datetime.datetime.now()-datetime.timedelta(days=1)).strftime("%Y%m%d*")
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        NoticeFetcher(notice_repository=NoticeRepository(mongodb_client=mongodb_client),
                      ted_api_adapter=TedAPIAdapter(request_api=TedRequestAPI())).fetch_notices_by_date_wild_card(
            wildcard_date=current_datetime_wildcard)

    @task
    def index_notices():
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        notices = notice_repository.get_notice_by_status(notice_status=NoticeStatus.RAW)
        for notice in notices:
            indexed_notice = index_notice(notice=notice)
            notice_repository.update(notice=indexed_notice)

    @task
    def trigger_document_proc_pipeline():
        context = get_current_context()
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        notices = notice_repository.get_notice_by_status(notice_status=NoticeStatus.RAW)
        for notice in notices:
            TriggerDagRunOperator(
                task_id=f'trigger_worker_dag_{notice.ted_id}',
                trigger_dag_id="worker_single_notice_process_orchestrator",
                conf={"notice_id": notice.ted_id,
                      "notice_status": str(notice.status)
                      }
            ).execute(context=context)

    fetch_notice_from_ted() >> index_notices() >> trigger_document_proc_pipeline()


dag = selector_daily_fetch_orchestrator()
