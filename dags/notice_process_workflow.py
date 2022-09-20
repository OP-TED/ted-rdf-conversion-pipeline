from airflow.operators.python import get_current_context, BranchPythonOperator

from dags import DEFAULT_DAG_ARGUMENTS
from airflow.decorators import dag, task

from dags.dags_utils import push_dag_downstream
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


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     max_active_runs=256,
     max_active_tasks=256,
     tags=['worker', 'pipeline'])
def notice_process_workflow():
    """

    """

    def _start_processing():
        context = get_current_context()
        dag_params = context["dag_run"].conf
        push_dag_downstream(key=NOTICE_IDS_KEY, value=dag_params[NOTICE_IDS_KEY])
        return dag_params[START_WITH_STEP_NAME_KEY]

    def _selector_branch_before_transformation():


    def _selector_branch_before_validation():
        ...

    def _selector_branch_before_package():
        ...

    def _selector_branch_before_publish():
        ...

    def _stop_processing():
        """

        """

    start_processing = BranchPythonOperator(
        task_id=START_PROCESSING_TASK_ID,
        python_callable=_start_processing,
    )

    start_processing = BranchPythonOperator(
        task_id=START_PROCESSING_TASK_ID,
        python_callable=_selector_branch_before_transformation,
    )

    start_processing = BranchPythonOperator(
        task_id=START_PROCESSING_TASK_ID,
        python_callable=_start_processing,
    )
    start_processing = BranchPythonOperator(
        task_id=START_PROCESSING_TASK_ID,
        python_callable=_start_processing,
    )
    start_processing = BranchPythonOperator(
        task_id=START_PROCESSING_TASK_ID,
        python_callable=_start_processing,
    )
    start_processing = BranchPythonOperator(
        task_id=START_PROCESSING_TASK_ID,
        python_callable=_start_processing,
    )

    stop_processing = BranchPythonOperator(
        task_id=STOP_PROCESSING_TASK_ID,
        python_callable=_stop_processing,
    )


    notice_normalisation_step = NoticeBatchPipelineOperator(task_id=NOTICE_NORMALISATION_PIPELINE_TASK_ID,
                                                            python_callable=notice_normalisation_pipeline
                                                            )

    notice_transformation_step = NoticeBatchPipelineOperator(task_id=NOTICE_TRANSFORMATION_PIPELINE_TASK_ID,
                                                             python_callable=notice_transformation_pipeline
                                                             )

    notice_validation_step = NoticeBatchPipelineOperator(task_id=NOTICE_VALIDATION_PIPELINE_TASK_ID,
                                                         python_callable=notice_validation_pipeline
                                                         )
    notice_package_step = NoticeBatchPipelineOperator(task_id=NOTICE_PACKAGE_PIPELINE_TASK_ID,
                                                      python_callable=notice_package_pipeline
                                                      )

    notice_publish_step = NoticeBatchPipelineOperator(task_id=NOTICE_PUBLISH_PIPELINE_TASK_ID,
                                                      python_callable=notice_publish_pipeline
                                                      )




worker_dag = notice_process_workflow()
