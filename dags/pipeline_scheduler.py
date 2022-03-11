import locale
import sys
sys.path.append("/opt/airflow/")
sys.path = list(set(sys.path))
import os
os.chdir("/opt/airflow/")


from airflow.decorators import dag, task
from airflow.operators.python import get_current_context

from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from datetime import datetime, timedelta
from dags import DEFAULT_DAG_ARGUMENTS

@dag(default_args=DEFAULT_DAG_ARGUMENTS, tags=['master', 'pipeline','scheduler'])
def pipeline_scheduler():

    @task
    def trigger_notice_fetcher():
        context = get_current_context()
        yesterday_date = datetime.now() - timedelta(1)
        fetch_time_filter = "20220203*" #yesterday_date.strftime("%Y%m%d")+"*" #"20220203*"
        print(f"Generated wildcard is :{fetch_time_filter}")
        TriggerDagRunOperator(
            task_id='trigger_worker_dag_1',
            trigger_dag_id="notice_fetcher_master",
        conf={"fetch_time_filter": fetch_time_filter}
        ).execute(context = context)


    trigger_notice_fetcher()


etl_dag = pipeline_scheduler()