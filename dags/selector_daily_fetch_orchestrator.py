import sys

from ted_sws.core.model.notice import NoticeStatus

sys.path.append("/opt/airflow/")
sys.path = list(set(sys.path))
import os
os.chdir("/opt/airflow/")

from dags import DEFAULT_DAG_ARGUMENTS
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from pymongo import MongoClient

from ted_sws import config
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, TedRequestAPI
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher

@dag(default_args=DEFAULT_DAG_ARGUMENTS, tags=['selector', 'daily-fetch'])
def selector_daily_fetch_orchestrator():
    @task
    def fetch_notice_from_ted():
        context = get_current_context()
        dag_conf = context["dag_run"].conf
        key = 'fetch_time_filter'
        if key in dag_conf.keys():
            print(dag_conf[key])
            mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
            NoticeFetcher(notice_repository=NoticeRepository(mongodb_client=mongodb_client),
                          ted_api_adapter=TedAPIAdapter(request_api=TedRequestAPI())).fetch_notices_by_date_wild_card(
                wildcard_date=dag_conf[key]) #"20220203*"
        else:
            print(f"The key={key} is not present in context")



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
                      "notice_status": notice.status
                      }
            ).execute(context=context)

    fetch_notice_from_ted()
    trigger_document_proc_pipeline()


etl_dag = selector_daily_fetch_orchestrator()
