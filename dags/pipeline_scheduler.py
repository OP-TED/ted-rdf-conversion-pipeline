
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from datetime import datetime, timedelta

from airflow.operators.trigger_dagrun import TriggerDagRunOperator

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


@dag(default_args=DEFAULT_DAG_ARGUMENTS, tags=['master', 'pipeline','scheduler'])
def pipeline_scheduler():

    @task
    def trigger_notice_fetcher():
        context = get_current_context()
        fetch_time_filter = "WILD_CARD" #TODO: generate wild_card by current date
        TriggerDagRunOperator(
            task_id='trigger_worker_dag_1',
            trigger_dag_id="notice_fetcher_master",
            conf={"fetch_time_filter": fetch_time_filter}
        ).execute(context = context['dag_run'])

    trigger_notice_fetcher()


etl_dag = pipeline_scheduler()