"""
This DAG is used to re-validate notices.
"""

from airflow.decorators import dag, task
from airflow.models import Param

from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import push_dag_downstream, get_dag_param
from dags.notice_processing_pipeline import NOTICE_TRANSFORMATION_PIPELINE_TASK_ID
from dags.operators.DagBatchPipelineOperator import NOTICE_IDS_KEY, TriggerNoticeBatchPipelineOperator
from dags.pipelines.notice_selectors_pipelines import notice_ids_selector_by_status
from dags.reprocess_dag_params import REPROCESS_DAG_PARAMS, FORM_NUMBER_DAG_PARAM, START_DATE_DAG_PARAM, \
    END_DATE_DAG_PARAM, XSD_VERSION_DAG_PARAM, RE_NORMALISE_TARGET_NOTICE_STATES, RE_TRANSFORM_TARGET_NOTICE_STATES, \
    RE_PACKAGE_TARGET_NOTICE_STATES, RE_PROCESS_PUBLISHED_PUBLICLY_AVAILABLE_TARGET_NOTICE_STATES, \
    RE_PUBLISH_TARGET_NOTICE_STATES
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.event_manager.adapters.event_log_decorator import event_log
from ted_sws.event_manager.model.event_message import TechnicalEventMessage, EventMessageMetadata, \
    EventMessageProcessType

DAG_NAME = "reprocess_backlog"

RE_VALIDATE_TARGET_NOTICE_STATES = [NoticeStatus.DISTILLED]
TRIGGER_NOTICE_PROCESS_WORKFLOW_TASK_ID = "trigger_notice_process_workflow"

REPROCESS_TYPE_MAP = {"unnormalised": RE_NORMALISE_TARGET_NOTICE_STATES,
                      "untransformed": RE_TRANSFORM_TARGET_NOTICE_STATES,
                      "unvalidated": RE_VALIDATE_TARGET_NOTICE_STATES,
                      "unpackaged": RE_PACKAGE_TARGET_NOTICE_STATES,
                      "unpublished": RE_PUBLISH_TARGET_NOTICE_STATES,
                      "publicly available": RE_PROCESS_PUBLISHED_PUBLICLY_AVAILABLE_TARGET_NOTICE_STATES}


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     description=__doc__[0: __doc__.find(".")],
     doc_md=__doc__,
     tags=['selector', 're-validate'],
     params={**REPROCESS_DAG_PARAMS,
             "reprocess_type": Param(default="unnormalised", title="Reprocess Type",
                                     enum=list(REPROCESS_TYPE_MAP.keys()))
             }
     )
def reprocess_backlog():
    @task
    @event_log(TechnicalEventMessage(
        message="select_notices_for_re_processing",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def select_notices_for_re_validate():
        form_number = get_dag_param(key=FORM_NUMBER_DAG_PARAM)
        start_date = get_dag_param(key=START_DATE_DAG_PARAM)
        end_date = get_dag_param(key=END_DATE_DAG_PARAM)
        xsd_version = get_dag_param(key=XSD_VERSION_DAG_PARAM)
        reprocess_type = get_dag_param(key="reprocess_type")

        notice_ids = notice_ids_selector_by_status(notice_statuses=REPROCESS_TYPE_MAP[reprocess_type],
                                                   form_number=form_number, start_date=start_date,
                                                   end_date=end_date, xsd_version=xsd_version)
        push_dag_downstream(key=NOTICE_IDS_KEY, value=notice_ids)

    trigger_notice_process_workflow = TriggerNoticeBatchPipelineOperator(
        task_id=TRIGGER_NOTICE_PROCESS_WORKFLOW_TASK_ID,
        start_with_step_name=NOTICE_TRANSFORMATION_PIPELINE_TASK_ID
    )
    select_notices_for_re_validate() >> trigger_notice_process_workflow


dag = reprocess_backlog()
