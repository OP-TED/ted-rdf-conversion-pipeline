import datetime

from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.utils.types import NOTSET

from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import get_dag_param

DAG_NAME = "test_dag_a"
FORM_NUMBER_DAG_PARAM = "form_number"
START_DATE_DAG_PARAM = "start_date"
END_DATE_DAG_PARAM = "end_date"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     tags=['test', 'new-ui'],
     params={
         FORM_NUMBER_DAG_PARAM: Param(
             default=None,
             type=["null", "string"],
             title="Form number",
             description="""Form number of the notice"""),
         START_DATE_DAG_PARAM: Param(
             default=None,
             type=["null", "string"],
             format="date",
             title="Date Picker",
             description="Please select a date, use the button on the left for a pup-up calendar. "
                         "See that here are no times!",
         ),
         END_DATE_DAG_PARAM: Param(
             default=f"{datetime.date.today()}",
             type=["null", "string"],
             format="date",
             title="Date Picker",
             description="Please select a date, use the button on the left for a pup-up calendar. "
                         "See that here are no times!",
         ),
     }
     )
def test_dag_a():
    @task
    def print_configs():
        form_number = get_dag_param(key=FORM_NUMBER_DAG_PARAM)
        start_date = get_dag_param(key=START_DATE_DAG_PARAM)
        end_date = get_dag_param(key=END_DATE_DAG_PARAM)
        print(f"form_number: {form_number}")
        print(f"start_date: {start_date}")
        print(f"end_date: {end_date}")

    print_configs()


dag = test_dag_a()
