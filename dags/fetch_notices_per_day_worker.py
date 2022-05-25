from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from dags import DEFAULT_DAG_ARGUMENTS
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from pymongo import MongoClient

from ted_sws import config
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository

from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, TedRequestAPI
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher

DATE_WILD_CARD_KEY = "date_wild_card"


@dag(default_args=DEFAULT_DAG_ARGUMENTS, schedule_interval=None, tags=['worker', 'fetch_notices_per_day'])
def fetch_notices_per_day_worker():
    @task
    def fetch_notices():
        context = get_current_context()
        dag_conf = context["dag_run"].conf

        if DATE_WILD_CARD_KEY not in dag_conf.keys():
            raise "Config key [date] is not present in dag context"

        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        NoticeFetcher(notice_repository=NoticeRepository(mongodb_client=mongodb_client),
                      ted_api_adapter=TedAPIAdapter(request_api=TedRequestAPI())).fetch_notices_by_date_wild_card(
            wildcard_date=dag_conf[DATE_WILD_CARD_KEY])  # "20220203*"

    @task
    def trigger_index_and_normalise_notice_worker():
        context = get_current_context()
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        notices = notice_repository.get_notice_by_status(notice_status=NoticeStatus.RAW)
        for notice in notices:
            TriggerDagRunOperator(
                task_id=f'trigger_index_and_normalise_notice_worker_dag_{notice.ted_id}',
                trigger_dag_id="index_and_normalise_notice_worker",
                conf={"notice_id": notice.ted_id}
            ).execute(context=context)

    fetch_notices() >> trigger_index_and_normalise_notice_worker()


dag = fetch_notices_per_day_worker()
