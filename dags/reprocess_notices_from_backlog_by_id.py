from airflow.decorators import dag, task
from airflow.models import Param

from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import push_dag_downstream, get_dag_param
from dags.operators.DagBatchPipelineOperator import NOTICE_IDS_KEY, TriggerNoticeBatchPipelineOperator
from dags.notice_processing_pipeline import NOTICE_TRANSFORMATION_PIPELINE_TASK_ID
from ted_sws.event_manager.adapters.event_log_decorator import event_log
from ted_sws.event_manager.model.event_message import TechnicalEventMessage, EventMessageMetadata, EventMessageProcessType

DAG_ID = "reprocess_notices_by_id_from_backlog"
DAG_NAME = "Reprocess notices from backlog by ID"

NOTICE_IDS_DAG_PARAM = "notice_ids"
TRIGGER_NOTICE_PROCESS_WORKFLOW_TASK_ID = "trigger_notice_process_workflow"

@dag(
    default_args=DEFAULT_DAG_ARGUMENTS,
    dag_id=DAG_ID,
    dag_display_name=DAG_NAME,
    schedule_interval=None,
    tags=["selector", "re-transform"],
    params={
        NOTICE_IDS_DAG_PARAM: Param(
            type="array",
            title="Notice IDs",
            description="Required. List of TED Notice IDs to reprocess. Each value should be entered on a new line. Example: [\"123456-2022\", \"456789-2023\"]. Every ID value should be entered on a newline"
        )
    },
    description=DAG_NAME
)
def reprocess_notices_by_id_from_backlog():
    @task
    @event_log(TechnicalEventMessage(
        message="select_notices_for_reprocess_by_id",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG,
            process_name=DAG_ID
        ))
    )
    def select_notice_ids():
        notice_ids = get_dag_param(key=NOTICE_IDS_DAG_PARAM, raise_error=True)

        if not notice_ids:
            raise Exception("No notice IDs provided.")

        push_dag_downstream(key=NOTICE_IDS_KEY, value=notice_ids)

    trigger_notice_process_workflow = TriggerNoticeBatchPipelineOperator(
        task_id=TRIGGER_NOTICE_PROCESS_WORKFLOW_TASK_ID,
        start_with_step_name=NOTICE_TRANSFORMATION_PIPELINE_TASK_ID
    )

    select_notice_ids() >> trigger_notice_process_workflow

dag = reprocess_notices_by_id_from_backlog()