from airflow.decorators import dag, task
from airflow.models import Param

from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import push_dag_downstream, get_dag_param
from dags.notice_processing_pipeline import NOTICE_NORMALISATION_PIPELINE_TASK_ID
from dags.operators.DagBatchPipelineOperator import NOTICE_IDS_KEY, TriggerNoticeBatchPipelineOperator
from dags.pipelines.notice_selectors_pipelines import notice_ids_selector_by_status
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.event_manager.adapters.event_log_decorator import event_log
from ted_sws.event_manager.model.event_message import TechnicalEventMessage, EventMessageMetadata, EventMessageProcessType

DAG_ID = "reprocess_notices_from_backlog_by_status"
DAG_NAME = "Reprocess notices from backlog by status"

TRIGGER_NOTICE_PROCESS_WORKFLOW_TASK_ID = "trigger_notice_process_workflow"
START_DATE_DAG_PARAM = "start_date"
END_DATE_DAG_PARAM = "end_date"
NOTICE_STATUSES_DAG_PARAM = "notice_statuses"


@dag(
    default_args=DEFAULT_DAG_ARGUMENTS,
    dag_id=DAG_ID,
    dag_display_name=DAG_NAME,
    schedule_interval=None,
    tags=['selector', 're-transform'],
    params={

        NOTICE_STATUSES_DAG_PARAM: Param(
            default=[],
            type="array",
            title="Notice Statuses",
            description="Required. Select one or more notice statuses to reprocess.",
            examples=[status.name for status in NoticeStatus]
        ),
        START_DATE_DAG_PARAM: Param(default="", type=["null", "string"], format="date", description="Start publication date (YYYY-MM-DD)"),
        END_DATE_DAG_PARAM: Param(default="", type=["null", "string"], format="date", description="End publication date (YYYY-MM-DD)")
    }
    )
def reprocess_notices_from_backlog_by_status():
    @task
    @event_log(TechnicalEventMessage(
        message="select_notices_for_re_transform",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG,
            process_name=DAG_ID
        ))
    )
    def select_notices_for_re_transform():
        start_date = get_dag_param(key=START_DATE_DAG_PARAM, default_value="")
        end_date = get_dag_param(key=END_DATE_DAG_PARAM,default_value="")
        statuses_param = get_dag_param(key=NOTICE_STATUSES_DAG_PARAM)

        notice_statuses = [NoticeStatus[status_str] for status_str in statuses_param]

        notice_ids = notice_ids_selector_by_status(
            notice_statuses=notice_statuses,
            start_date=start_date,
            end_date=end_date
        )

        push_dag_downstream(key=NOTICE_IDS_KEY, value=notice_ids)

    trigger_notice_process_workflow = TriggerNoticeBatchPipelineOperator(
        task_id=TRIGGER_NOTICE_PROCESS_WORKFLOW_TASK_ID,
        start_with_step_name=NOTICE_NORMALISATION_PIPELINE_TASK_ID
    )

    select_notices_for_re_transform() >> trigger_notice_process_workflow

dag = reprocess_notices_from_backlog_by_status()