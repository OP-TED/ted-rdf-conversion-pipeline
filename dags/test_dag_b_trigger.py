import datetime
from uuid import uuid4

from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from dags import DEFAULT_DAG_ARGUMENTS

DAG_NAME = "test_dag_b_trigger"
FORM_NUMBER_DAG_PARAM = "form_number"
START_DATE_DAG_PARAM = "start_date"
END_DATE_DAG_PARAM = "end_date"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     tags=['test', 'new-ui'],
     # params={
     #     FORM_NUMBER_DAG_PARAM: Param(
     #         default=None,
     #         type=["null", "string"],
     #         title="Form number",
     #         description="""Form number of the notice"""),
     #     START_DATE_DAG_PARAM: Param(
     #         default=None,
     #         type=["null", "string"],
     #         format="date",
     #         title="Date Picker",
     #         description="Please select a date, use the button on the left for a pup-up calendar. "
     #                     "See that here are no times!",
     #     ),
     #     END_DATE_DAG_PARAM: Param(
     #         default=f"{datetime.date.today()}",
     #         type=["null", "string"],
     #         format="date",
     #         title="Date Picker",
     #         description="Please select a date, use the button on the left for a pup-up calendar. "
     #                     "See that here are no times!",
     #     ),
     # }
     )
def test_dag_b():
    @task
    def trigger_test_dag_a():
        context = get_current_context()
        TriggerDagRunOperator(
            task_id=f'trigger_worker_dag_{uuid4().hex}',
            trigger_dag_id="test_dag_a",
            conf={
                FORM_NUMBER_DAG_PARAM: "test_form_number",
            }
        ).execute(context=context)

    trigger_test_dag_a()


dag = test_dag_b()
