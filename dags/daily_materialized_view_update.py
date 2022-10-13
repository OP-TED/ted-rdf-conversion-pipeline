from airflow.decorators import dag, task
from pymongo import MongoClient

from dags import DEFAULT_DAG_ARGUMENTS
from ted_sws import config
from ted_sws.data_manager.services.create_notice_collection_materialised_view import \
    create_notice_collection_materialised_view

DAG_NAME = "daily_materialized_view_update"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     catchup=False,
     schedule_interval="0 5 * * *",
     tags=['mongodb', 'daily-views-update'])
def daily_materialized_view_update():
    @task
    def update_materialized_view():
        create_notice_collection_materialised_view(mongo_client=MongoClient(config.MONGO_DB_AUTH_URL))

    update_materialized_view()


dag = daily_materialized_view_update()
