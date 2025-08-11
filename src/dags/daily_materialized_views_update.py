from airflow.decorators import dag, task
from pymongo import MongoClient

from src.dags import DEFAULT_DAG_ARGUMENTS, NOTICES_COLLECTION_DATASET, MATERIALISED_VIEW_DATASET
from src.ted_sws import config
from src.ted_sws.data_manager.services.create_batch_collection_materialised_view import \
    create_batch_collection_materialised_view
from src.ted_sws.data_manager.services.create_notice_collection_materialised_view import \
    create_notice_collection_materialised_view, create_notice_kpi_collection

DAILY_MATERIALISED_VIEWS_DAG_NAME = "daily_materialized_views_update"
DAILY_MATERIALISED_VIEWS_MAX_ACTIVE_RUNS: int = 1
DAG_NAME = "Materialized views update"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     dag_id=DAILY_MATERIALISED_VIEWS_DAG_NAME,
     dag_display_name=DAG_NAME,
     catchup=False,
     schedule=NOTICES_COLLECTION_DATASET,
     max_active_runs=DAILY_MATERIALISED_VIEWS_MAX_ACTIVE_RUNS,
     tags=['mongodb', 'daily-views-update'])
def daily_materialized_views_update():
    @task(inlets=[NOTICES_COLLECTION_DATASET])
    def create_materialised_view():
        mongo_client = MongoClient(config.MONGO_DB_AUTH_URL)
        create_notice_collection_materialised_view(mongo_client=mongo_client)

    @task(inlets=[NOTICES_COLLECTION_DATASET])
    def create_kpi_collection_for_notices():
        mongo_client = MongoClient(config.MONGO_DB_AUTH_URL)
        create_notice_kpi_collection(mongo_client=mongo_client)

    @task(inlets=[NOTICES_COLLECTION_DATASET], outlets=[MATERIALISED_VIEW_DATASET])
    def aggregate_batch_logs():
        mongo_client = MongoClient(config.MONGO_DB_AUTH_URL)
        create_batch_collection_materialised_view(mongo_client=mongo_client)

    create_materialised_view() >> create_kpi_collection_for_notices() >> aggregate_batch_logs()


dag = daily_materialized_views_update()
