import sys

sys.path.append("/opt/airflow/")
sys.path = list(set(sys.path))
import os

os.chdir("/opt/airflow/")

from pymongo import MongoClient

from ted_sws import config
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryMongoDB
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapper
import ted_sws.notice_transformer.services.notice_transformer as notice_transformer

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context

from datetime import datetime, timedelta

DEFAULT_DAG_ARGUMENTS = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime.now(),
    "email": ["info@meaningfy.ws"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=3600),
    "schedule_interval": "@once",
    "max_active_runs": 128,
    "concurrency": 128,
    "execution_timeout": timedelta(hours=24),
}


@dag(default_args=DEFAULT_DAG_ARGUMENTS, tags=['worker', 'pipeline'])
def notice_transformer_dag():
    @task
    def get_dag_params():
        context = get_current_context()
        return context["dag_run"].conf

    @task
    def transform_notice(params):
        notice_id = params["notice_id"]
        mapping_suite_id = params["mapping_suite_id"]
        mongo_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_repository = NoticeRepository(mongodb_client=mongo_client)
        notice = notice_repository.get(reference=notice_id)
        mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongo_client)
        mapping_suite = mapping_suite_repository.get(reference=mapping_suite_id)
        result_notice = notice_transformer.transform_notice(notice=notice, mapping_suite=mapping_suite,
                                                            rml_mapper=RMLMapper(
                                                                rml_mapper_path=config.RML_MAPPER_PATH
                                                            ))
        # TODO: revise config.RML_MAPPER_PATH for execution in Airflow
        notice_repository.update(notice=result_notice)

    dag_params = get_dag_params()
    transform_notice(dag_params)


# dag = notice_transformer_dag()
