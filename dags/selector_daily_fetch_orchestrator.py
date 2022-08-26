from datetime import datetime, timedelta
from typing import List

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from pymongo import MongoClient

from dags import DEFAULT_DAG_ARGUMENTS
from ted_sws import config
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.event_manager.adapters.event_log_decorator import event_log
from ted_sws.event_manager.model.event_message import TechnicalEventMessage, EventMessageMetadata, \
    EventMessageProcessType
from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, TedRequestAPI
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher
from ted_sws.supra_notice_manager.services.daily_supra_notice_manager import \
    create_and_store_in_mongo_db_daily_supra_notice

DAG_NAME = "selector_daily_fetch_orchestrator"
WILD_CARD_PARAM = "wild_card"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     catchup=False,
     schedule_interval="0 3 * * *",
     tags=['selector', 'daily-fetch'])
def selector_daily_fetch_orchestrator():
    @task
    @event_log(TechnicalEventMessage(
        message="fetch_notice_from_ted",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def fetch_notice_from_ted():
        context = get_current_context()
        dag_params = context["dag_run"].conf
        if WILD_CARD_PARAM in dag_params.keys():
            current_datetime_wildcard = dag_params[WILD_CARD_PARAM]
        else:
            current_datetime_wildcard = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d*")
        notice_publication_date = datetime.strptime(current_datetime_wildcard, "%Y%m%d*").date()
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_ids = NoticeFetcher(notice_repository=NoticeRepository(mongodb_client=mongodb_client),
                                   ted_api_adapter=TedAPIAdapter(
                                       request_api=TedRequestAPI())).fetch_notices_by_date_wild_card(
            wildcard_date=current_datetime_wildcard)
        create_and_store_in_mongo_db_daily_supra_notice(notice_ids=notice_ids, mongodb_client=mongodb_client,
                                                        notice_fetched_date=notice_publication_date)
        return notice_ids

    @task
    @event_log(TechnicalEventMessage(
        message="trigger_document_proc_pipeline",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def trigger_document_proc_pipeline(notice_ids: List[str]):
        context = get_current_context()
        for notice_id in notice_ids:
            TriggerDagRunOperator(
                task_id=f'trigger_worker_dag_{notice_id}',
                trigger_dag_id="worker_single_notice_process_orchestrator",
                conf={"notice_id": notice_id,
                      "notice_status": str(NoticeStatus.RAW)
                      }
            ).execute(context=context)

    trigger_document_proc_pipeline(fetch_notice_from_ted())


dag = selector_daily_fetch_orchestrator()
