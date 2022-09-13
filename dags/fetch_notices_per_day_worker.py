from datetime import datetime

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
from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, TedRequestAPI
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher
from ted_sws.notice_metadata_processor.services.metadata_normalizer import normalise_notice
from ted_sws.supra_notice_manager.services.daily_supra_notice_manager import \
    create_and_store_in_mongo_db_daily_supra_notice

DAG_NAME = "fetch_notices_per_day_worker"
DATE_WILD_CARD_KEY = "date_wild_card"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     max_active_runs=144,
     max_active_tasks=144,
     schedule_interval=None,
     tags=['worker', 'fetch_notices_per_day'])
def fetch_notices_per_day_worker():
    @task
    @event_log(TechnicalEventMessage(
        message="fetch_notices_and_index_and_normalise_each_notice",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def fetch_notices_and_index_and_normalise_each_notice():
        context = get_current_context()
        dag_conf = context["dag_run"].conf

        if DATE_WILD_CARD_KEY not in dag_conf.keys():
            raise Exception(f"Config key {DATE_WILD_CARD_KEY} is not present in dag context")

        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        notice_ids = NoticeFetcher(notice_repository=notice_repository,
                                   ted_api_adapter=TedAPIAdapter(
                                       request_api=TedRequestAPI())).fetch_notices_by_date_wild_card(
            wildcard_date=dag_conf[DATE_WILD_CARD_KEY])  # "20220203*"
        notice_publication_date = datetime.strptime(dag_conf[DATE_WILD_CARD_KEY], "%Y%m%d*").date()
        create_and_store_in_mongo_db_daily_supra_notice(notice_ids=notice_ids, mongodb_client=mongodb_client,
                                                        notice_fetched_date=notice_publication_date)
        for notice_id in notice_ids:
            notice = notice_repository.get(reference=notice_id)
            notice = index_notice(notice=notice)
            try:
                normalised_notice = normalise_notice(notice=notice)
                notice_repository.update(notice=normalised_notice)
            except Exception as e:
                log_error(message=str(e))

    fetch_notices_and_index_and_normalise_each_notice()


dag = fetch_notices_per_day_worker()
