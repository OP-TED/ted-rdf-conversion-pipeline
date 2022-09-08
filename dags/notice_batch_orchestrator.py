from itertools import chain, islice
from typing import Iterator

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from pymongo import MongoClient

from dags import DEFAULT_DAG_ARGUMENTS
from dags.notice_batch_worker import NOTICE_BATCH_KEY
from ted_sws import config
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository, NOTICE_STATUS
from ted_sws.event_manager.adapters.event_log_decorator import event_log
from ted_sws.event_manager.model.event_message import TechnicalEventMessage, EventMessageMetadata, \
    EventMessageProcessType

DAG_NAME = "notice_batch_orchestrator"

NOTICE_STATUS_KEY = "notice_status"
NOTICE_BATCH_SIZE_KEY = "notice_batch_size"
NOTICE_BATCH_SIZE_DEFAULT = 5000
NOTICE_STATUS_VALUE_DEFAULT = "RAW"


def chunks(iterable, chunk_size: int):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, chunk_size - 1))


def get_notice_ids(notice_repository: NoticeRepository, notice_status: str) -> Iterator[str]:
    for result_dict in notice_repository.collection.find({NOTICE_STATUS: notice_status}, {"ted_id": 1}):
        yield result_dict["ted_id"]


@dag(default_args=DEFAULT_DAG_ARGUMENTS, schedule_interval=None, tags=['master', 'notice_batch_orchestrator'])
def notice_batch_orchestrator():
    @task
    @event_log(TechnicalEventMessage(
        message="generate_notice_batches_and_trigger_worker",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def generate_notice_batches_and_trigger_worker():
        context = get_current_context()
        dag_conf = context["dag_run"].conf

        notice_status = dag_conf[
            NOTICE_STATUS_KEY] if NOTICE_STATUS_KEY in dag_conf.keys() else NOTICE_STATUS_VALUE_DEFAULT
        notice_batch_size = dag_conf[
            NOTICE_BATCH_SIZE_KEY] if NOTICE_BATCH_SIZE_KEY in dag_conf.keys() else NOTICE_BATCH_SIZE_DEFAULT

        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        notice_batch_counter = 0
        for notice_batch in chunks(get_notice_ids(notice_repository=notice_repository,
                                                  notice_status=notice_status),
                                   chunk_size=notice_batch_size):
            TriggerDagRunOperator(
                task_id=f'trigger_notice_batch_worker_dag_{notice_batch_counter}',
                trigger_dag_id="notice_batch_worker",
                conf={NOTICE_BATCH_KEY: [notice.ted_id for notice in notice_batch]}
            ).execute(context=context)
            notice_batch_counter += 1

    generate_notice_batches_and_trigger_worker()


dag = notice_batch_orchestrator()
