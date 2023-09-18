"""
This DAG is responsible for fetching notices from TED by query.
"""

from datetime import date

from airflow.decorators import dag, task
from airflow.models import Param
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.utils.trigger_rule import TriggerRule
from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import get_dag_param, push_dag_downstream, pull_dag_upstream
from dags.operators.DagBatchPipelineOperator import NOTICE_IDS_KEY, TriggerNoticeBatchPipelineOperator
from dags.pipelines.notice_fetcher_pipelines import notice_fetcher_by_query_pipeline
from ted_sws.event_manager.adapters.event_log_decorator import event_log
from ted_sws.event_manager.model.event_message import TechnicalEventMessage, EventMessageMetadata, \
    EventMessageProcessType

DAG_NAME = "fetch_notices_by_query"
BATCH_SIZE = 2000
QUERY_DAG_KEY = "query"
TRIGGER_COMPLETE_WORKFLOW_DAG_KEY = "trigger_complete_workflow"
TRIGGER_PARTIAL_WORKFLOW_TASK_ID = "trigger_partial_notice_proc_workflow"
TRIGGER_COMPLETE_WORKFLOW_TASK_ID = "trigger_complete_notice_proc_workflow"
CHECK_IF_TRIGGER_COMPLETE_WORKFLOW_TASK_ID = "check_if_trigger_complete_workflow"
FINISH_FETCH_BY_DATE_TASK_ID = "finish_fetch_by_query"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     tags=['fetch'],
     description=__doc__[0: __doc__.find(".")],
     doc_md=__doc__,
     params={
         QUERY_DAG_KEY: Param(
             default=f"PD=[>={date.today().strftime('%Y%m%d')} AND <={date.today().strftime('%Y%m%d')}]",
             type="string",
             title="Query",
             description="""This field is required.
                Query to fetch notices from TED."""
         ),
         TRIGGER_COMPLETE_WORKFLOW_DAG_KEY: Param(
             default=True,
             type="boolean",
             title="Trigger Complete Workflow",
             description="""This field is required.
                If true, the complete workflow will be triggered, otherwise only the partial workflow will be triggered."""
         )
     }
     )
def fetch_notices_by_query():
    @task
    @event_log(TechnicalEventMessage(
        message="fetch_by_query_notice_from_ted",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def fetch_by_query_notice_from_ted():
        notice_ids = notice_fetcher_by_query_pipeline(query=get_dag_param(key=QUERY_DAG_KEY, raise_error=True))
        if not notice_ids:
            raise Exception("No notices has been fetched!")
        push_dag_downstream(key=NOTICE_IDS_KEY, value=notice_ids)

    trigger_complete_workflow = TriggerNoticeBatchPipelineOperator(task_id=TRIGGER_COMPLETE_WORKFLOW_TASK_ID,
                                                                   execute_only_one_step=False
                                                                   )
    trigger_normalisation_workflow = TriggerNoticeBatchPipelineOperator(
        task_id=TRIGGER_PARTIAL_WORKFLOW_TASK_ID,
        batch_size=BATCH_SIZE,
        execute_only_one_step=True)

    def _branch_selector():
        trigger_complete_workflow = get_dag_param(key=TRIGGER_COMPLETE_WORKFLOW_DAG_KEY,
                                                  default_value=True)
        push_dag_downstream(key=NOTICE_IDS_KEY, value=pull_dag_upstream(key=NOTICE_IDS_KEY))
        if trigger_complete_workflow:
            return [TRIGGER_COMPLETE_WORKFLOW_TASK_ID]
        return [TRIGGER_PARTIAL_WORKFLOW_TASK_ID]

    branch_task = BranchPythonOperator(
        task_id=CHECK_IF_TRIGGER_COMPLETE_WORKFLOW_TASK_ID,
        python_callable=_branch_selector,
    )

    finish_step = EmptyOperator(task_id=FINISH_FETCH_BY_DATE_TASK_ID,
                                trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)

    fetch_by_query_notice_from_ted() >> branch_task >> [trigger_normalisation_workflow,
                                                        trigger_complete_workflow] >> finish_step


dag = fetch_notices_by_query()
