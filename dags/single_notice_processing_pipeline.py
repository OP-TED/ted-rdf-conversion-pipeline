import random
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator, get_current_context
from airflow.utils.edgemodifier import Label
from airflow.utils.trigger_rule import TriggerRule

from dags import DEFAULT_DAG_ARGUMENTS


def first_step(task_instance):
    context = get_current_context()
    conf = context["dag_run"].conf
    print("option = ", conf["option"])
    task_instance.xcom_push(key="option", value=conf["option"])


def branch_selector(task_instance):
    option = task_instance.xcom_pull(key="option", task_ids=["run_this_first"])
    print("branch selector option : ", option)
    return option


with DAG(
        dag_id="single_notice_processing_pipeline",
        default_args=DEFAULT_DAG_ARGUMENTS,
        tags=['notice_processing_pipeline', 'worker'],
) as dag:
    run_this_first = PythonOperator(
        task_id='run_this_first',
        python_callable=first_step
    )

    options = ['branch_a', 'branch_b', 'branch_c', 'branch_d']

    branching = BranchPythonOperator(
        task_id='branching',
        python_callable=branch_selector,
    )
    run_this_first >> branching

    join = DummyOperator(
        task_id='join',
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    for option in options:
        t = DummyOperator(
            task_id=option,
        )

        dummy_follow = DummyOperator(
            task_id='follow_' + option,
        )

        # Label is optional here, but it can help identify more complex branches
        branching >> Label(option) >> t >> dummy_follow >> join
