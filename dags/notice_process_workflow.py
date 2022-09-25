from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.decorators import dag
from airflow.utils.trigger_rule import TriggerRule

from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import push_dag_downstream, get_dag_param
from dags.operators.DagBatchPipelineOperator import NoticeBatchPipelineOperator, NOTICE_IDS_KEY
from dags.pipelines.notice_processor_pipelines import notice_normalisation_pipeline, notice_transformation_pipeline, \
    notice_validation_pipeline, notice_package_pipeline, notice_publish_pipeline

START_WITH_STEP_NAME_KEY = "start_with_step_name"
EXECUTE_ONLY_ONE_STEP_KEY = "execute_only_one_step"

NOTICE_NORMALISATION_PIPELINE_TASK_ID = "notice_normalisation_pipeline"
NOTICE_TRANSFORMATION_PIPELINE_TASK_ID = "notice_transformation_pipeline"
NOTICE_VALIDATION_PIPELINE_TASK_ID = "notice_validation_pipeline"
NOTICE_PACKAGE_PIPELINE_TASK_ID = "notice_package_pipeline"
NOTICE_PUBLISH_PIPELINE_TASK_ID = "notice_publish_pipeline"
START_PROCESSING_TASK_ID = 'start_processing'
STOP_PROCESSING_TASK_ID = "stop_processing"
SELECTOR_BRANCH_BEFORE_TRANSFORMATION_TASK_ID = "selector_branch_before_transformation"
SELECTOR_BRANCH_BEFORE_VALIDATION_TASK_ID = "selector_branch_before_validation"
SELECTOR_BRANCH_BEFORE_PACKAGE_TASK_ID = "selector_branch_before_package"
SELECTOR_BRANCH_BEFORE_PUBLISH_TASK_ID = "selector_branch_before_publish"
DAG_NAME = "notice_process_workflow"

@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     max_active_runs=256,
     max_active_tasks=256,
     tags=['worker', 'pipeline'])
def notice_process_workflow():
    """

    """

    def _start_processing():
        notice_ids = get_dag_param(key=NOTICE_IDS_KEY, raise_error=True)
        start_with_step_name = get_dag_param(key=START_WITH_STEP_NAME_KEY,
                                             default_value=NOTICE_NORMALISATION_PIPELINE_TASK_ID)
        push_dag_downstream(key=NOTICE_IDS_KEY, value=notice_ids)
        return start_with_step_name

    def _selector_branch_before_transformation():
        return STOP_PROCESSING_TASK_ID if get_dag_param(
            key=EXECUTE_ONLY_ONE_STEP_KEY) else NOTICE_TRANSFORMATION_PIPELINE_TASK_ID

    def _selector_branch_before_validation():
        return STOP_PROCESSING_TASK_ID if get_dag_param(
            key=EXECUTE_ONLY_ONE_STEP_KEY) else NOTICE_VALIDATION_PIPELINE_TASK_ID

    def _selector_branch_before_package():
        return STOP_PROCESSING_TASK_ID if get_dag_param(
            key=EXECUTE_ONLY_ONE_STEP_KEY) else NOTICE_PACKAGE_PIPELINE_TASK_ID

    def _selector_branch_before_publish():
        return STOP_PROCESSING_TASK_ID if get_dag_param(
            key=EXECUTE_ONLY_ONE_STEP_KEY) else NOTICE_PUBLISH_PIPELINE_TASK_ID


    start_processing = BranchPythonOperator(
        task_id=START_PROCESSING_TASK_ID,
        python_callable=_start_processing,
    )

    selector_branch_before_transformation = BranchPythonOperator(
        task_id=SELECTOR_BRANCH_BEFORE_TRANSFORMATION_TASK_ID,
        python_callable=_selector_branch_before_transformation,
    )

    selector_branch_before_validation = BranchPythonOperator(
        task_id=SELECTOR_BRANCH_BEFORE_VALIDATION_TASK_ID,
        python_callable=_selector_branch_before_validation,
    )

    selector_branch_before_package = BranchPythonOperator(
        task_id=SELECTOR_BRANCH_BEFORE_PACKAGE_TASK_ID,
        python_callable=_selector_branch_before_package,
    )

    selector_branch_before_publish = BranchPythonOperator(
        task_id=SELECTOR_BRANCH_BEFORE_PUBLISH_TASK_ID,
        python_callable=_selector_branch_before_publish,
    )

    stop_processing = DummyOperator(
        task_id=STOP_PROCESSING_TASK_ID,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS
    )


    notice_normalisation_step = NoticeBatchPipelineOperator(python_callable=notice_normalisation_pipeline,
                                                            task_id=NOTICE_NORMALISATION_PIPELINE_TASK_ID,
                                                            trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS
                                                            )

    notice_transformation_step = NoticeBatchPipelineOperator(task_id=NOTICE_TRANSFORMATION_PIPELINE_TASK_ID,
                                                             python_callable=notice_transformation_pipeline,
                                                             trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS
                                                             )

    notice_validation_step = NoticeBatchPipelineOperator(task_id=NOTICE_VALIDATION_PIPELINE_TASK_ID,
                                                         python_callable=notice_validation_pipeline,
                                                         trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS
                                                         )
    notice_package_step = NoticeBatchPipelineOperator(task_id=NOTICE_PACKAGE_PIPELINE_TASK_ID,
                                                      python_callable=notice_package_pipeline,
                                                      trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS
                                                      )

    notice_publish_step = NoticeBatchPipelineOperator(task_id=NOTICE_PUBLISH_PIPELINE_TASK_ID,
                                                      python_callable=notice_publish_pipeline,
                                                      trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS
                                                      )

    start_processing >> [notice_normalisation_step, notice_transformation_step, notice_validation_step,
                         notice_package_step, notice_publish_step]
    [selector_branch_before_transformation, selector_branch_before_validation,
     selector_branch_before_package, selector_branch_before_publish, notice_publish_step] >> stop_processing
    notice_normalisation_step >> selector_branch_before_transformation >> notice_transformation_step
    notice_transformation_step >> selector_branch_before_validation >> notice_validation_step
    notice_validation_step >> selector_branch_before_package >> notice_package_step
    notice_package_step >> selector_branch_before_publish >> notice_publish_step


dag = notice_process_workflow()
