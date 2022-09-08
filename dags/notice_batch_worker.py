from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from pymongo import MongoClient

from dags import DEFAULT_DAG_ARGUMENTS
from ted_sws import config
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_sampler.services.notice_xml_indexer import index_notice
from ted_sws.event_manager.adapters.event_log_decorator import event_log
from ted_sws.event_manager.model.event_message import TechnicalEventMessage, EventMessageMetadata, \
    EventMessageProcessType
from ted_sws.event_manager.services.log import log_error
from ted_sws.notice_metadata_processor.services.metadata_normalizer import normalise_notice

DAG_NAME = "notice_batch_worker"

NOTICE_BATCH_KEY = "notice_batch"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     max_active_runs=256,
     max_active_tasks=256,
     tags=['master', 'notice_batch_worker'])
def notice_batch_worker():
    @task
    @event_log(TechnicalEventMessage(
        message="process_notice_batch",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def process_notice_batch():
        context = get_current_context()
        dag_conf = context["dag_run"].conf

        if NOTICE_BATCH_KEY not in dag_conf.keys():
            raise f"Config key [{NOTICE_BATCH_KEY}] is not present in dag context"

        notice_ids_batch = dag_conf[NOTICE_BATCH_KEY]
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)

        for notice_id in notice_ids_batch:
            notice = notice_repository.get(reference=notice_id)
            notice = index_notice(notice=notice)
            try:
                normalised_notice = normalise_notice(notice=notice)
                notice_repository.update(notice=normalised_notice)
            except Exception as e:
                log_error(message=str(e))

    process_notice_batch()


dag = notice_batch_worker()
