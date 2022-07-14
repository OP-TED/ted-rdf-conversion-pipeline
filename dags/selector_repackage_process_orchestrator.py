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

DAG_NAME = "selector_re_package_process_orchestrator"

RE_PACKAGE_TARGET_NOTICE_STATES = [NoticeStatus.ELIGIBLE_FOR_PACKAGING, NoticeStatus.INELIGIBLE_FOR_PUBLISHING]


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     tags=['selector', 're-package'])
def selector_re_package_process_orchestrator():
    @task
    @event_log(TechnicalEventMessage(
        message="select_notices_for_re_package_and_reset_status",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def select_notices_for_re_package_and_reset_status():
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        for target_notice_state in RE_PACKAGE_TARGET_NOTICE_STATES:
            notices = notice_repository.get_notice_by_status(notice_status=target_notice_state)
            for notice in notices:
                notice.update_status_to(new_status=NoticeStatus.ELIGIBLE_FOR_PACKAGING)
                notice_repository.update(notice=notice)

    @task
    @event_log(TechnicalEventMessage(
        message="trigger_worker_for_package_branch",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def trigger_worker_for_package_branch():
        context = get_current_context()
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        notices = notice_repository.get_notice_by_status(notice_status=NoticeStatus.ELIGIBLE_FOR_PACKAGING)
        for notice in notices:
            TriggerDagRunOperator(
                task_id=f'trigger_worker_dag_{notice.ted_id}',
                trigger_dag_id="worker_single_notice_process_orchestrator",
                conf={"notice_id": notice.ted_id,
                      "notice_status": str(notice.status)
                      }
            ).execute(context=context)

    select_notices_for_re_package_and_reset_status() >> trigger_worker_for_package_branch()


etl_dag = selector_re_package_process_orchestrator()
