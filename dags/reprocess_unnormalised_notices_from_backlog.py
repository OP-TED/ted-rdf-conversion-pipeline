"""
This DAG is used to reprocess all notices in RAW status from the backlog.
"""

from airflow.decorators import dag, task
from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import push_dag_downstream, get_dag_param
from dags.operators.DagBatchPipelineOperator import TriggerNoticeBatchPipelineOperator, NOTICE_IDS_KEY
from dags.pipelines.notice_selectors_pipelines import notice_ids_selector_by_status
from ted_sws.event_manager.adapters.event_log_decorator import event_log
from ted_sws.event_manager.model.event_message import TechnicalEventMessage, EventMessageMetadata, \
    EventMessageProcessType
from dags.reprocess_dag_params import START_DATE_DAG_PARAM, END_DATE_DAG_PARAM, REPROCESS_DATE_RANGE_DAG_PARAMS, \
    RE_NORMALISE_TARGET_NOTICE_STATES

DAG_NAME = "reprocess_unnormalised_notices_from_backlog"

TRIGGER_NOTICE_PROCESS_WORKFLOW_TASK_ID = "trigger_notice_process_workflow"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     description=__doc__[0: __doc__.find(".")],
     doc_md=__doc__,
     tags=['selector', 'raw-notices'],
     params=REPROCESS_DATE_RANGE_DAG_PARAMS
     )
def reprocess_unnormalised_notices_from_backlog():
    @task
    @event_log(TechnicalEventMessage(
        message="select_all_raw_notices",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def select_all_raw_notices():
        start_date = get_dag_param(key=START_DATE_DAG_PARAM)
        end_date = get_dag_param(key=END_DATE_DAG_PARAM)
        notice_ids = notice_ids_selector_by_status(notice_statuses=RE_NORMALISE_TARGET_NOTICE_STATES,
                                                   start_date=start_date,
                                                   end_date=end_date)
        push_dag_downstream(key=NOTICE_IDS_KEY, value=notice_ids)

    trigger_notice_process_workflow = TriggerNoticeBatchPipelineOperator(
        task_id=TRIGGER_NOTICE_PROCESS_WORKFLOW_TASK_ID
    )
    select_all_raw_notices() >> trigger_notice_process_workflow


dag = reprocess_unnormalised_notices_from_backlog()
