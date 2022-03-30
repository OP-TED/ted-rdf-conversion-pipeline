import sys

from ted_sws.core.model.notice import NoticeStatus

sys.path.append("/opt/airflow/")
sys.path = list(set(sys.path))
import os

os.chdir("/opt/airflow/")

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context, BranchPythonOperator, PythonOperator

from dags import DEFAULT_DAG_ARGUMENTS


def select_first_non_none(data):
    return next((item for item in data if item is not None), None)


def pull(key, task_ids=None):
    context = get_current_context()
    return select_first_non_none(
        context['ti'].xcom_pull(key=str(key), task_ids=task_ids if task_ids else context['task'].upstream_task_ids))


def push(key, value):
    context = get_current_context()
    return context['ti'].xcom_push(key=str(key), value=value)


@dag(default_args=DEFAULT_DAG_ARGUMENTS, tags=['worker', 'pipeline'])
def single_notice_proc_pipeline():

    def _normalise_notice_metadata():
        notice_id = pull(NoticeStatus.RAW)
        print(notice_id)
        notice_id = notice_id + "_normalised"
        push(NoticeStatus.NORMALISED_METADATA, notice_id)

    def _check_eligibility_for_transformation():
        notice_id = pull(NoticeStatus.NORMALISED_METADATA)
        print(notice_id)
        notice_id = notice_id + "_checked"
        push(f"notice_id_{NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION}", notice_id)
        push(f"mapping_suite_id_{NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION}", "mapping_suite_id")

    def _transform_notice():
        notice_id = pull(f"notice_id_{NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION}")
        mapping_suite_id = pull(f"mapping_suite_id_{NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION}")
        print(notice_id, mapping_suite_id)
        notice_id = notice_id + "_transformed"
        push(NoticeStatus.TRANSFORMED, notice_id)

    state_skip_table = {
        str(NoticeStatus.RAW): "normalise_notice_metadata",
        str(NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION): "check_eligibility_for_transformation",
        str(NoticeStatus.INELIGIBLE_FOR_PACKAGING): "transform_notice",
        str(NoticeStatus.VALIDATED): "transform_notice",
        str(NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION): "transform_notice"
    }

    normalise_notice_metadata = PythonOperator(
        task_id="normalise_notice_metadata",
        python_callable=_normalise_notice_metadata
    )
    check_eligibility_for_transformation = PythonOperator(
        task_id="check_eligibility_for_transformation",
        python_callable=_check_eligibility_for_transformation
    )
    transform_notice = PythonOperator(
        task_id="transform_notice",
        python_callable=_transform_notice
    )

    normalise_notice_metadata >> check_eligibility_for_transformation >> transform_notice

    def _get_task_run():
        context = get_current_context()
        dag_params = context["dag_run"].conf
        push(key=dag_params["notice_status"], value=dag_params["notice_id"])
        return state_skip_table[dag_params["notice_status"]]

    branch_task = BranchPythonOperator(
        task_id='start_processing_notice',
        python_callable=_get_task_run,
    )

    branch_task >> [normalise_notice_metadata, check_eligibility_for_transformation, transform_notice]


dag = single_notice_proc_pipeline()
