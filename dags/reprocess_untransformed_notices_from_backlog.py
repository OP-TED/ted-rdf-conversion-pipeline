"""
This DAG is used to re-transform notices.
"""

from airflow.decorators import dag, task
from airflow.models import Param

from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import push_dag_downstream, get_dag_param
from dags.notice_processing_pipeline import NOTICE_TRANSFORMATION_PIPELINE_TASK_ID
from dags.operators.DagBatchPipelineOperator import NOTICE_IDS_KEY, TriggerNoticeBatchPipelineOperator
from dags.pipelines.notice_selectors_pipelines import notice_ids_selector_by_status, \
    notice_ids_selector_by_mapping_suite_id
from dags.reprocess_dag_params import REPROCESS_DAG_PARAMS, FORM_NUMBER_DAG_PARAM, START_DATE_DAG_PARAM, \
    END_DATE_DAG_PARAM, XSD_VERSION_DAG_PARAM
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.event_manager.adapters.event_log_decorator import event_log
from ted_sws.event_manager.model.event_message import TechnicalEventMessage, EventMessageMetadata, \
    EventMessageProcessType

DAG_NAME = "reprocess_untransformed_notices_from_backlog"

MAPPING_SUITE_ID_DAG_PARAM = "mapping_suite_id"

RE_TRANSFORM_TARGET_NOTICE_STATES = [NoticeStatus.NORMALISED_METADATA, NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION,
                                     NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION,
                                     NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION,
                                     NoticeStatus.TRANSFORMED, NoticeStatus.DISTILLED
                                     ]
TRIGGER_NOTICE_PROCESS_WORKFLOW_TASK_ID = "trigger_notice_process_workflow"

RE_TRANSFORM_DAG_PARAMS = {**REPROCESS_DAG_PARAMS,
    MAPPING_SUITE_ID_DAG_PARAM: Param(
        default=None,
        type=["null", "string"],
        format="string",
        title="Mapping Suite ID",
        description="This field is optional. If you want to filter transformed notices by Mapping Suite ID, please insert a  Mapping Suite ID."
    )
}


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     description=__doc__[0: __doc__.find(".")],
     doc_md=__doc__,
     tags=['selector', 're-transform'],
     params=REPROCESS_DAG_PARAMS
     )
def reprocess_untransformed_notices_from_backlog():
    @task
    @event_log(TechnicalEventMessage(
        message="select_notices_for_re_transform",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def select_notices_for_re_transform():
        form_number = get_dag_param(key=FORM_NUMBER_DAG_PARAM)
        start_date = get_dag_param(key=START_DATE_DAG_PARAM)
        end_date = get_dag_param(key=END_DATE_DAG_PARAM)
        xsd_version = get_dag_param(key=XSD_VERSION_DAG_PARAM)
        mapping_suite_id = get_dag_param(key=MAPPING_SUITE_ID_DAG_PARAM)
        notice_ids = notice_ids_selector_by_status(notice_statuses=RE_TRANSFORM_TARGET_NOTICE_STATES,
                                                   form_number=form_number, start_date=start_date,
                                                   end_date=end_date, xsd_version=xsd_version)
        if mapping_suite_id:
            filtered_notice_ids_by_mapping_suite_id = notice_ids_selector_by_mapping_suite_id(mapping_suite_id=mapping_suite_id)
            notice_ids = list(set(notice_ids).intersection(set(filtered_notice_ids_by_mapping_suite_id)))
        push_dag_downstream(key=NOTICE_IDS_KEY, value=notice_ids)

    trigger_notice_process_workflow = TriggerNoticeBatchPipelineOperator(
        task_id=TRIGGER_NOTICE_PROCESS_WORKFLOW_TASK_ID,
        start_with_step_name=NOTICE_TRANSFORMATION_PIPELINE_TASK_ID
    )
    select_notices_for_re_transform() >> trigger_notice_process_workflow


dag = reprocess_untransformed_notices_from_backlog()
