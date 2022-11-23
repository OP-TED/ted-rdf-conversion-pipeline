from airflow.operators.python import PythonOperator
from airflow.decorators import dag
from airflow.utils.trigger_rule import TriggerRule

from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import get_dag_param, smart_xcom_push, smart_xcom_pull
from dags.operators.DagBatchPipelineOperator import NoticeBatchPipelineOperator, NOTICE_IDS_KEY
from dags.pipelines.notice_batch_processor_pipelines import notices_batch_distillation_pipeline
from dags.pipelines.notice_processor_pipelines import notice_transformation_pipeline
from dags.pipelines.notice_selectors_pipelines import notice_ids_selector_by_status
from ted_sws.core.model.notice import NoticeStatus

NOTICE_NORMALISATION_PIPELINE_TASK_ID = "notice_normalisation_pipeline"
NOTICE_TRANSFORMATION_PIPELINE_TASK_ID = "notice_transformation_pipeline"
NOTICE_DISTILLATION_PIPELINE_TASK_ID = "notice_distillation_pipeline"

STOP_PROCESSING_TASK_ID = "stop_processing"
BRANCH_SELECTOR_TASK_ID = 'start_processing'
DAG_NAME = "ted_data_notice_process_workflow"


FORM_NUMBER_DAG_PARAM = "form_number"
START_DATE_DAG_PARAM = "start_date"
END_DATE_DAG_PARAM = "end_date"
XSD_VERSION_DAG_PARAM = "xsd_version"


RE_TRANSFORM_TARGET_NOTICE_STATES = [NoticeStatus.NORMALISED_METADATA, NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION,
                                     NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION, NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION,
                                     NoticeStatus.TRANSFORMED, NoticeStatus.DISTILLED
                                     ]

@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     max_active_runs=1,
     max_active_tasks=256,
     tags=['ted-data', 'worker', 'pipeline'])
def ted_data_notice_process_workflow():
    """

    """

    def _start_processing():
        form_number = get_dag_param(key=FORM_NUMBER_DAG_PARAM)
        start_date = get_dag_param(key=START_DATE_DAG_PARAM)
        end_date = get_dag_param(key=END_DATE_DAG_PARAM)
        xsd_version = get_dag_param(key=XSD_VERSION_DAG_PARAM)
        notice_ids = notice_ids_selector_by_status(notice_statuses=RE_TRANSFORM_TARGET_NOTICE_STATES,
                                                   form_number=form_number, start_date=start_date,
                                                   end_date=end_date, xsd_version=xsd_version)
        smart_xcom_push(key=NOTICE_IDS_KEY, value=notice_ids)

    def _stop_processing():
        notice_ids = smart_xcom_pull(key=NOTICE_IDS_KEY)
        if not notice_ids:
            raise Exception(f"No notice has been processed!")

    start_processing = PythonOperator(
        task_id=BRANCH_SELECTOR_TASK_ID,
        python_callable=_start_processing,
    )

    stop_processing = PythonOperator(
        task_id=STOP_PROCESSING_TASK_ID,
        python_callable=_stop_processing
    )

    notice_transformation_step = NoticeBatchPipelineOperator(notice_pipeline_callable=notice_transformation_pipeline,
                                                             task_id=NOTICE_TRANSFORMATION_PIPELINE_TASK_ID,
                                                             trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)

    notice_distillation_step = NoticeBatchPipelineOperator(batch_pipeline_callable=notices_batch_distillation_pipeline,
                                                           task_id=NOTICE_DISTILLATION_PIPELINE_TASK_ID,
                                                           trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS
                                                           )

    start_processing >> notice_transformation_step >> notice_distillation_step >> stop_processing


dag = ted_data_notice_process_workflow()
