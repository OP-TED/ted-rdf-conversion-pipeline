import sys
from random import randint

sys.path.append("/opt/airflow/")
sys.path = list(set(sys.path))
import os
os.chdir("/opt/airflow/")

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


@dag(default_args=DEFAULT_DAG_ARGUMENTS, tags=['kolea', 'example-dag'])
def transformer_dag():

    def get_number_of_documents():
        # API call
        return int(randint(2,6))

    @task
    def second_step(data = "Default value"):
        print(data)

    @task
    def first_step():
        #context = get_current_context()
        return "Salut Kolea"

    #tmp_var = first_step()
    #second_step(tmp_var)
    #second_step(first_step())
    number_of_documents = get_number_of_documents()
    for index in range(0,int(number_of_documents)):
        second_step(first_step())


dag = transformer_dag()
