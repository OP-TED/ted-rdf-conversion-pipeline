from airflow.decorators import dag, task
from pymongo import MongoClient

from dags import DEFAULT_DAG_ARGUMENTS
from ted_sws import config
from ted_sws.data_manager.services.create_batch_collection_materialised_view import \
    create_batch_collection_materialised_view
from ted_sws.data_manager.services.create_notice_collection_materialised_view import \
    create_notice_collection_materialised_view, create_notice_kpi_collection

DAG_NAME = "daily_materialized_view_update"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     catchup=False,
     schedule_interval="0 6 * * *",
     tags=['mongodb', 'daily-views-update'])
def daily_materialized_view_update():
    @task
    def create_materialised_view():
        mongo_client = MongoClient(config.MONGO_DB_AUTH_URL)
        create_notice_collection_materialised_view(mongo_client=mongo_client)

    @task
    def create_kpi_collection_for_notices():
        mongo_client = MongoClient(config.MONGO_DB_AUTH_URL)
        create_notice_kpi_collection(mongo_client=mongo_client)

    @task
    def aggregate_batch_logs():
        mongo_client = MongoClient(config.MONGO_DB_AUTH_URL)
        create_batch_collection_materialised_view(mongo_client=mongo_client)

    create_materialised_view() >> create_kpi_collection_for_notices() >> aggregate_batch_logs()


dag = daily_materialized_view_update()
