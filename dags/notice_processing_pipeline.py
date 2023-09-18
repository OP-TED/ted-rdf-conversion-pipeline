"""
This DAG is used to process notices in batch mode.
"""

from typing import List

from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.decorators import dag
from airflow.utils.trigger_rule import TriggerRule

from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import get_dag_param, smart_xcom_push, smart_xcom_forward, smart_xcom_pull
from dags.operators.DagBatchPipelineOperator import NoticeBatchPipelineOperator, NOTICE_IDS_KEY, \
    EXECUTE_ONLY_ONE_STEP_KEY, START_WITH_STEP_NAME_KEY, AIRFLOW_NUMBER_OF_WORKERS
from dags.pipelines.notice_batch_processor_pipelines import notices_batch_distillation_pipeline, \
    notice_batch_transformer_pipeline
from dags.pipelines.notice_processor_pipelines import notice_normalisation_pipeline, notice_validation_pipeline, \
    notice_package_pipeline, notice_publish_pipeline

NOTICE_NORMALISATION_PIPELINE_TASK_ID = "notice_normalisation_pipeline"
NOTICE_TRANSFORMATION_PIPELINE_TASK_ID = "notice_transformation_pipeline"
NOTICE_DISTILLATION_PIPELINE_TASK_ID = "notice_distillation_pipeline"
NOTICE_VALIDATION_PIPELINE_TASK_ID = "notice_validation_pipeline"
NOTICE_PACKAGE_PIPELINE_TASK_ID = "notice_package_pipeline"
NOTICE_PUBLISH_PIPELINE_TASK_ID = "notice_publish_pipeline"
STOP_PROCESSING_TASK_ID = "stop_processing"
BRANCH_SELECTOR_TASK_ID = 'branch_selector'
SELECTOR_BRANCH_BEFORE_TRANSFORMATION_TASK_ID = "switch_to_transformation"
SELECTOR_BRANCH_BEFORE_VALIDATION_TASK_ID = "switch_to_validation"
SELECTOR_BRANCH_BEFORE_PACKAGE_TASK_ID = "switch_to_package"
SELECTOR_BRANCH_BEFORE_PUBLISH_TASK_ID = "switch_to_publish"
DAG_NAME = "notice_processing_pipeline"

BRANCH_SELECTOR_MAP = {NOTICE_NORMALISATION_PIPELINE_TASK_ID: NOTICE_NORMALISATION_PIPELINE_TASK_ID,
                       NOTICE_TRANSFORMATION_PIPELINE_TASK_ID: SELECTOR_BRANCH_BEFORE_TRANSFORMATION_TASK_ID,
                       NOTICE_VALIDATION_PIPELINE_TASK_ID: SELECTOR_BRANCH_BEFORE_VALIDATION_TASK_ID,
                       NOTICE_PACKAGE_PIPELINE_TASK_ID: SELECTOR_BRANCH_BEFORE_PACKAGE_TASK_ID,
                       NOTICE_PUBLISH_PIPELINE_TASK_ID: SELECTOR_BRANCH_BEFORE_PUBLISH_TASK_ID
                       }


def branch_selector(result_branch: str, xcom_forward_keys: List[str] = [NOTICE_IDS_KEY]) -> str:
    start_with_step_name = get_dag_param(key=START_WITH_STEP_NAME_KEY,
                                         default_value=NOTICE_NORMALISATION_PIPELINE_TASK_ID)
    if start_with_step_name != result_branch:
        result_branch = STOP_PROCESSING_TASK_ID if get_dag_param(key=EXECUTE_ONLY_ONE_STEP_KEY) else result_branch
    for xcom_forward_key in xcom_forward_keys:
        smart_xcom_forward(key=xcom_forward_key, destination_task_id=result_branch)
    return result_branch


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     description=__doc__[0: __doc__.find(".")],
     doc_md=__doc__,
     max_active_runs=AIRFLOW_NUMBER_OF_WORKERS,
     max_active_tasks=1,
     tags=['worker', 'pipeline'])
def notice_processing_pipeline():
    """

    """

    def _start_processing():
        notice_ids = get_dag_param(key=NOTICE_IDS_KEY, raise_error=True)
        start_with_step_name = get_dag_param(key=START_WITH_STEP_NAME_KEY,
                                             default_value=NOTICE_NORMALISATION_PIPELINE_TASK_ID)
        task_id = BRANCH_SELECTOR_MAP[start_with_step_name]
        smart_xcom_push(key=NOTICE_IDS_KEY, value=notice_ids, destination_task_id=task_id)
        return task_id

    def _selector_branch_before_transformation():
        return branch_selector(NOTICE_TRANSFORMATION_PIPELINE_TASK_ID)

    def _selector_branch_before_validation():
        return branch_selector(NOTICE_VALIDATION_PIPELINE_TASK_ID)

    def _selector_branch_before_package():
        return branch_selector(NOTICE_PACKAGE_PIPELINE_TASK_ID)

    def _selector_branch_before_publish():
        return branch_selector(NOTICE_PUBLISH_PIPELINE_TASK_ID)

    def _stop_processing():
        notice_ids = smart_xcom_pull(key=NOTICE_IDS_KEY)
        if not notice_ids:
            raise Exception("No notice has been processed!")

    start_processing = BranchPythonOperator(
        task_id=BRANCH_SELECTOR_TASK_ID,
        python_callable=_start_processing,
    )

    selector_branch_before_transformation = BranchPythonOperator(
        task_id=SELECTOR_BRANCH_BEFORE_TRANSFORMATION_TASK_ID,
        python_callable=_selector_branch_before_transformation,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    selector_branch_before_validation = BranchPythonOperator(
        task_id=SELECTOR_BRANCH_BEFORE_VALIDATION_TASK_ID,
        python_callable=_selector_branch_before_validation,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    selector_branch_before_package = BranchPythonOperator(
        task_id=SELECTOR_BRANCH_BEFORE_PACKAGE_TASK_ID,
        python_callable=_selector_branch_before_package,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    selector_branch_before_publish = BranchPythonOperator(
        task_id=SELECTOR_BRANCH_BEFORE_PUBLISH_TASK_ID,
        python_callable=_selector_branch_before_publish,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    stop_processing = PythonOperator(
        task_id=STOP_PROCESSING_TASK_ID,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
        python_callable=_stop_processing
    )

    notice_normalisation_step = NoticeBatchPipelineOperator(notice_pipeline_callable=notice_normalisation_pipeline,
                                                            task_id=NOTICE_NORMALISATION_PIPELINE_TASK_ID,
                                                            trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)

    notice_transformation_step = NoticeBatchPipelineOperator(batch_pipeline_callable=notice_batch_transformer_pipeline,
                                                             task_id=NOTICE_TRANSFORMATION_PIPELINE_TASK_ID,
                                                             trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)

    notice_distillation_step = NoticeBatchPipelineOperator(batch_pipeline_callable=notices_batch_distillation_pipeline,
                                                           task_id=NOTICE_DISTILLATION_PIPELINE_TASK_ID,
                                                           trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS
                                                           )

    notice_validation_step = NoticeBatchPipelineOperator(notice_pipeline_callable=notice_validation_pipeline,
                                                         task_id=NOTICE_VALIDATION_PIPELINE_TASK_ID,
                                                         trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)
    notice_package_step = NoticeBatchPipelineOperator(notice_pipeline_callable=notice_package_pipeline,
                                                      task_id=NOTICE_PACKAGE_PIPELINE_TASK_ID,
                                                      trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)

    notice_publish_step = NoticeBatchPipelineOperator(notice_pipeline_callable=notice_publish_pipeline,
                                                      task_id=NOTICE_PUBLISH_PIPELINE_TASK_ID,
                                                      trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)

    start_processing >> [notice_normalisation_step, selector_branch_before_transformation,
                         selector_branch_before_validation,
                         selector_branch_before_package, selector_branch_before_publish]
    [selector_branch_before_transformation, selector_branch_before_validation,
     selector_branch_before_package, selector_branch_before_publish, notice_publish_step] >> stop_processing
    notice_normalisation_step >> selector_branch_before_transformation >> notice_transformation_step
    notice_transformation_step >> notice_distillation_step >> selector_branch_before_validation >> notice_validation_step
    notice_validation_step >> selector_branch_before_package >> notice_package_step
    notice_package_step >> selector_branch_before_publish >> notice_publish_step


dag = notice_processing_pipeline()
