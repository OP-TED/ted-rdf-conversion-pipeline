from datetime import timedelta, datetime
from airflow.decorators import dag, task
from pymongo import MongoClient
from ted_sws.event_manager.model.event_message import TechnicalEventMessage, EventMessageMetadata, \
    EventMessageProcessType
from ted_sws.event_manager.adapters.event_log_decorator import event_log

from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import get_dag_param

DAG_NAME = "notice_daily_validation_workflow"
NOTICE_PUBLICATION_DATE_DAG_CONF_KEY = "notice_publication_date"


def get_notice_publication_date():
    notice_publication_date = get_dag_param(key=NOTICE_PUBLICATION_DATE_DAG_CONF_KEY)
    if notice_publication_date:
        return datetime.strptime(notice_publication_date, "%Y%m%d")
    else:
        return datetime.now() - timedelta(days=2)


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     catchup=False,
     schedule_interval="0 1 * * *",
     tags=['selector', 'daily-validation'])
def notice_daily_validation_workflow():
    @task
    @event_log(TechnicalEventMessage(
        message="validate_fetched_notices",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def validate_fetched_notices():
        from ted_sws import config
        from ted_sws.supra_notice_manager.services.supra_notice_validator import validate_and_update_daily_supra_notice

        publication_date = get_notice_publication_date()
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        validate_and_update_daily_supra_notice(notice_publication_day=publication_date,
                                               mongodb_client=mongodb_client
                                               )

    @task
    @event_log(TechnicalEventMessage(
        message="summarize_validation_for_daily_supra_notice",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def summarize_validation_for_daily_supra_notice():
        from ted_sws import config
        from ted_sws.supra_notice_manager.services.supra_notice_validator import \
            summary_validation_for_daily_supra_notice

        publication_date = get_notice_publication_date()
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        summary_validation_for_daily_supra_notice(notice_publication_day=publication_date,
                                                  mongodb_client=mongodb_client
                                                  )

    @task
    @event_log(TechnicalEventMessage(
        message="validate_availability_of_notice_in_cellar",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def validate_availability_of_notice_in_cellar():
        from ted_sws import config
        from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
        from ted_sws.data_manager.adapters.supra_notice_repository import DailySupraNoticeRepository
        from ted_sws.notice_validator.services.check_availability_of_notice_in_cellar import \
            validate_notice_availability_in_cellar

        notice_publication_day = get_notice_publication_date()
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        repo = DailySupraNoticeRepository(mongodb_client=mongodb_client)
        supra_notice = repo.get(reference=notice_publication_day)
        if supra_notice:
            notice_repository = NoticeRepository(mongodb_client=mongodb_client)
            for notice_id in supra_notice.notice_ids:
                notice = notice_repository.get(reference=notice_id)
                old_notice_status = notice.status
                notice = validate_notice_availability_in_cellar(notice=notice)
                if notice.status != old_notice_status:
                    notice_repository.update(notice=notice)

    validate_fetched_notices() >> summarize_validation_for_daily_supra_notice() >> validate_availability_of_notice_in_cellar()


dag = notice_daily_validation_workflow()
