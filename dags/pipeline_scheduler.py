
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context

from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from dags import DEFAULT_DAG_ARGUMENTS


@dag(default_args=DEFAULT_DAG_ARGUMENTS, tags=['master', 'pipeline','scheduler'])
def pipeline_scheduler():

    @task
    def trigger_notice_fetcher():
        context = get_current_context()
        fetch_time_filter = "20220203*" #TODO: generate wild_card by current date
        TriggerDagRunOperator(
            task_id='trigger_worker_dag_1',
            trigger_dag_id="notice_fetcher_master",
            conf={"fetch_time_filter": fetch_time_filter}
        ).execute(context = context['dag_run'])

    trigger_notice_fetcher()


etl_dag = pipeline_scheduler()