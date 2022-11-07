from airflow.decorators import dag, task
from pymongo import MongoClient

from dags import DEFAULT_DAG_ARGUMENTS
from ted_sws import config
from ted_sws.data_manager.services.create_batch_collection_materialised_view import \
    create_batch_collection_materialised_view
from ted_sws.data_manager.services.create_dag_collection_materialised_view import \
    create_dag_collection_materialised_view
from ted_sws.data_manager.services.create_notice_collection_materialised_view import \
    create_notice_collection_materialised_view, update_notice_collection_materialised_view

DAG_NAME = "daily_materialized_view_update"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     catchup=False,
     schedule_interval="0 5 * * *",
     tags=['mongodb', 'daily-views-update'])
def daily_materialized_view_update():
    @task
    def create_materialised_view():
        mongo_client = MongoClient(config.MONGO_DB_AUTH_URL)
        create_notice_collection_materialised_view(mongo_client=mongo_client)

    @task
    def update_materialised_view_with_logs():
        mongo_client = MongoClient(config.MONGO_DB_AUTH_URL)
        update_notice_collection_materialised_view(mongo_client=mongo_client)
        create_batch_collection_materialised_view(mongo_client=mongo_client)

    @task
    def create_dag_materialised_view():
        mongo_client = MongoClient(config.MONGO_DB_AUTH_URL)
        create_dag_collection_materialised_view(mongo_client=mongo_client)

    create_materialised_view() >> update_materialised_view_with_logs() >> create_dag_materialised_view()


dag = daily_materialized_view_update()
