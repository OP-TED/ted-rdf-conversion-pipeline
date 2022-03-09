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
def document_proc_pipeline():
    @task
    def get_dag_params():
        context = get_current_context()
        return context["dag_run"].conf

    @task
    def load_notice(dag_params: dict):
        return dag_params["notice_id"]

    @task
    def normalise_notice_metadata(notice_id: str):
        print(notice_id)
        return notice_id + "_normalised"

    @task
    def transform_notice(notice_id: str):
        print(notice_id)
        return notice_id + "_transformed"

    @task
    def validate_resulting_rdf(notice_id: str):
        print(notice_id)
        return notice_id + "_validated"

    @task
    def package_notice(notice_id: str):
        print(notice_id)
        return notice_id + "_packaged"

    @task
    def publish_notice_in_cellar(notice_id: str):
        print(notice_id)
        return notice_id + "_published"

    dag_steps = [normalise_notice_metadata, transform_notice, validate_resulting_rdf, package_notice,
                 publish_notice_in_cellar]
    dag_params = get_dag_params()
    notice_id = load_notice(dag_params)
    for dag_step in dag_steps:
        notice_id = dag_step(notice_id)


dag = document_proc_pipeline()
