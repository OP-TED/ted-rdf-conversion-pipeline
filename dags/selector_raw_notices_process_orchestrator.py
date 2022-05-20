from dags import DEFAULT_DAG_ARGUMENTS
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from pymongo import MongoClient
from ted_sws.core.model.notice import NoticeStatus

from ted_sws import config
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository


@dag(default_args=DEFAULT_DAG_ARGUMENTS, tags=['selector', 'raw-notices'])
def selector_raw_notices_process_orchestrator():
    @task
    def trigger_worker_for_raw_notices():
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

    trigger_worker_for_raw_notices()


etl_dag = selector_raw_notices_process_orchestrator()
