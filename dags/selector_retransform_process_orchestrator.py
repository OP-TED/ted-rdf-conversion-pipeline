from airflow.decorators import dag, task

from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import push_dag_downstream
from dags.operators.DagBatchPipelineOperator import NOTICE_IDS_KEY, TriggerNoticeBatchPipelineOperator
from dags.pipelines.notice_selectors_pipelines import notice_ids_selector_by_status
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.event_manager.adapters.event_log_decorator import event_log
from ted_sws.event_manager.model.event_message import TechnicalEventMessage, EventMessageMetadata, \
    EventMessageProcessType

DAG_NAME = "selector_re_transform_process_orchestrator"

RE_TRANSFORM_TARGET_NOTICE_STATES = [NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION,
                                     NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION,
                                     NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION, NoticeStatus.TRANSFORMED,
                                     NoticeStatus.DISTILLED, NoticeStatus.VALIDATED,
                                     NoticeStatus.INELIGIBLE_FOR_PACKAGING
                                     ]
TRIGGER_NOTICE_PROCESS_WORKFLOW_TASK_ID = "trigger_notice_process_workflow"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     tags=['selector', 're-transform'])
def selector_re_transform_process_orchestrator():
    @task
    @event_log(TechnicalEventMessage(
        message="select_notices_for_re_transform",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def select_notices_for_re_transform():
        notice_ids = notice_ids_selector_by_status(notice_statuses=RE_TRANSFORM_TARGET_NOTICE_STATES)
        push_dag_downstream(key=NOTICE_IDS_KEY, value=notice_ids)

    trigger_notice_process_workflow = TriggerNoticeBatchPipelineOperator(
        task_id=TRIGGER_NOTICE_PROCESS_WORKFLOW_TASK_ID)
    select_notices_for_re_transform() >> trigger_notice_process_workflow


dag = selector_re_transform_process_orchestrator()
