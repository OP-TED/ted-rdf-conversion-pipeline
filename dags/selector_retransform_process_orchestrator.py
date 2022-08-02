from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from pymongo import MongoClient

from dags import DEFAULT_DAG_ARGUMENTS
from ted_sws import config
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.event_manager.adapters.event_log_decorator import event_log
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.model.event_message import TechnicalEventMessage, EventMessageMetadata, \
    EventMessageProcessType, EventMessage
from ted_sws.event_manager.services.logger_from_context import get_logger_from_dag_context

DAG_NAME = "selector_re_transform_process_orchestrator"

RE_TRANSFORM_TARGET_NOTICE_STATES = [NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION,
                                     NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION,
                                     NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION, NoticeStatus.TRANSFORMED,
                                     NoticeStatus.DISTILLED, NoticeStatus.VALIDATED,
                                     NoticeStatus.INELIGIBLE_FOR_PACKAGING
                                     ]


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     tags=['selector', 're-transform'])
def selector_re_transform_process_orchestrator():
    @task
    @event_log(TechnicalEventMessage(
        message="select_notices_for_re_transform_and_reset_status",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def select_notices_for_re_transform_and_reset_status(**context_args):
        event_logger: EventLogger = get_logger_from_dag_context(context_args)
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        for target_notice_state in RE_TRANSFORM_TARGET_NOTICE_STATES:
            event_logger.info(event_message=EventMessage(message=f"select notices with status : {target_notice_state}"))
            notices = notice_repository.get_notice_by_status(notice_status=target_notice_state)
            for notice in notices:
                notice.update_status_to(new_status=NoticeStatus.NORMALISED_METADATA)
                notice_repository.update(notice=notice)

    @task
    @event_log(TechnicalEventMessage(
        message="trigger_worker_for_transform_branch",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def trigger_worker_for_transform_branch():
        context = get_current_context()
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        notices = notice_repository.get_notice_by_status(notice_status=NoticeStatus.NORMALISED_METADATA)
        for notice in notices:
            TriggerDagRunOperator(
                task_id=f'trigger_worker_dag_{notice.ted_id}',
                trigger_dag_id="worker_single_notice_process_orchestrator",
                conf={"notice_id": notice.ted_id,
                      "notice_status": str(notice.status)
                      }
            ).execute(context=context)

    select_notices_for_re_transform_and_reset_status() >> trigger_worker_for_transform_branch()


etl_dag = selector_re_transform_process_orchestrator()
