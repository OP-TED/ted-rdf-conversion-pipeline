from dags import DEFAULT_DAG_ARGUMENTS
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from pymongo import MongoClient
from ted_sws import config
from ted_sws.mapping_suite_processor.services.conceptual_mapping_processor import \
    mapping_suite_processor_from_github_expand_and_load_package_in_mongo_db

MAPPING_SUITE_PACKAGE_NAME_DAG_PARAM_KEY = 'mapping_suite_package_name'


@dag(default_args=DEFAULT_DAG_ARGUMENTS, tags=['fetch', 'mapping-suite', 'github'])
def load_mapping_suite_in_mongodb():
    @task
    def fetch_mapping_suite_package_from_github_into_mongodb():
        context = get_current_context()
        dag_conf = context["dag_run"].conf
        key = MAPPING_SUITE_PACKAGE_NAME_DAG_PARAM_KEY
        if key in dag_conf.keys():
            mapping_suite_package_name = dag_conf[key]
            mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
            mapping_suite_processor_from_github_expand_and_load_package_in_mongo_db(
                mapping_suite_package_name=mapping_suite_package_name,
                mongodb_client=mongodb_client
            )
        else:
            print(f"The key={key} is not present in context")

    fetch_mapping_suite_package_from_github_into_mongodb()

dag = load_mapping_suite_in_mongodb()
