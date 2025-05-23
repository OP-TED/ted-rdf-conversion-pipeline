from typing import List

from airflow.decorators import dag
from airflow.exceptions import AirflowSkipException
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.utils.trigger_rule import TriggerRule

from dags import DEFAULT_DAG_ARGUMENTS, NOTICE_NORMALISATION_PIPELINE_TASK_ID, STOP_PROCESSING_TASK_ID, \
    BRANCH_SELECTOR_MAP, NOTICE_TRANSFORMATION_PIPELINE_TASK_ID, NOTICE_VALIDATION_PIPELINE_TASK_ID, \
    NOTICE_PACKAGE_PIPELINE_TASK_ID, NOTICE_PUBLISH_PIPELINE_TASK_ID, BRANCH_SELECTOR_TASK_ID, \
    SELECTOR_BRANCH_BEFORE_TRANSFORMATION_TASK_ID, SELECTOR_BRANCH_BEFORE_VALIDATION_TASK_ID, \
    SELECTOR_BRANCH_BEFORE_PACKAGE_TASK_ID, SELECTOR_BRANCH_BEFORE_PUBLISH_TASK_ID, \
    NOTICE_DISTILLATION_PIPELINE_TASK_ID, NOTICES_COLLECTION_DATASET
from dags.dags_utils import get_dag_param, smart_xcom_push, smart_xcom_forward, smart_xcom_pull
from dags.operators.DagBatchPipelineOperator import NoticeBatchPipelineOperator, NOTICE_IDS_KEY, \
    EXECUTE_ONLY_ONE_STEP_KEY, START_WITH_STEP_NAME_KEY
from dags.pipelines.notice_batch_processor_pipelines import notices_batch_distillation_pipeline
from dags.pipelines.notice_processor_pipelines import notice_normalisation_pipeline, notice_transformation_pipeline, \
    notice_validation_pipeline, notice_package_pipeline, notice_publish_pipeline

DAG_NAME = "notice_processing_pipeline"
DAG_ID = "notice_processing_pipeline"


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
     dag_display_name=DAG_NAME,
     dag_id=DAG_ID,
     max_active_runs=256,
     max_active_tasks=256,
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
        pass

    start_processing = BranchPythonOperator(
        task_id=BRANCH_SELECTOR_TASK_ID,
        python_callable=_start_processing,
        trigger_rule=TriggerRule.ALWAYS
    )

    selector_branch_before_transformation = BranchPythonOperator(
        task_id=SELECTOR_BRANCH_BEFORE_TRANSFORMATION_TASK_ID,
        python_callable=_selector_branch_before_transformation,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    selector_branch_before_validation = BranchPythonOperator(
        task_id=SELECTOR_BRANCH_BEFORE_VALIDATION_TASK_ID,
        python_callable=_selector_branch_before_validation,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    selector_branch_before_package = BranchPythonOperator(
        task_id=SELECTOR_BRANCH_BEFORE_PACKAGE_TASK_ID,
        python_callable=_selector_branch_before_package,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    selector_branch_before_publish = BranchPythonOperator(
        task_id=SELECTOR_BRANCH_BEFORE_PUBLISH_TASK_ID,
        python_callable=_selector_branch_before_publish,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    stop_processing = PythonOperator(
        task_id=STOP_PROCESSING_TASK_ID,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
        python_callable=_stop_processing,
        outlets=NOTICES_COLLECTION_DATASET
    )

    notice_normalisation_step = NoticeBatchPipelineOperator(notice_pipeline_callable=notice_normalisation_pipeline,
                                                            task_id=NOTICE_NORMALISATION_PIPELINE_TASK_ID,
                                                            trigger_rule=TriggerRule.ALL_SUCCESS)

    notice_transformation_step = NoticeBatchPipelineOperator(notice_pipeline_callable=notice_transformation_pipeline,
                                                             task_id=NOTICE_TRANSFORMATION_PIPELINE_TASK_ID,
                                                             trigger_rule=TriggerRule.ALL_SUCCESS)

    notice_distillation_step = NoticeBatchPipelineOperator(batch_pipeline_callable=notices_batch_distillation_pipeline,
                                                           task_id=NOTICE_DISTILLATION_PIPELINE_TASK_ID,
                                                           trigger_rule=TriggerRule.ALL_SUCCESS
                                                           )

    notice_validation_step = NoticeBatchPipelineOperator(notice_pipeline_callable=notice_validation_pipeline,
                                                         task_id=NOTICE_VALIDATION_PIPELINE_TASK_ID,
                                                         trigger_rule=TriggerRule.ALL_SUCCESS)
    notice_package_step = NoticeBatchPipelineOperator(notice_pipeline_callable=notice_package_pipeline,
                                                      task_id=NOTICE_PACKAGE_PIPELINE_TASK_ID,
                                                      trigger_rule=TriggerRule.ALL_SUCCESS)

    notice_publish_step = NoticeBatchPipelineOperator(notice_pipeline_callable=notice_publish_pipeline,
                                                      task_id=NOTICE_PUBLISH_PIPELINE_TASK_ID,
                                                      trigger_rule=TriggerRule.ALL_SUCCESS)

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
