from airflow.decorators import dag, task
from pymongo import MongoClient

from dags import DEFAULT_DAG_ARGUMENTS
from ted_sws import config
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.notice_validator.services.check_availability_of_notice_in_cellar import \
    validate_notices_availability_in_cellar

DAG_NAME = "daily_check_notices_availability_in_cellar"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     catchup=False,
     schedule_interval="0 0 * * *",
     tags=['daily', 'validation'])
def daily_check_notices_availability_in_cellar():
    @task
    def check_notices_availability_in_cellar():
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        validate_notices_availability_in_cellar(notice_statuses=[NoticeStatus.PUBLISHED,
                                                                 NoticeStatus.PUBLICLY_UNAVAILABLE],
                                                mongodb_client=mongodb_client)

    check_notices_availability_in_cellar()


dag = daily_check_notices_availability_in_cellar()
