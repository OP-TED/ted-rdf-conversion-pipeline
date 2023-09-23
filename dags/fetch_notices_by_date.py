"""
This DAG is used to fetch notices from TED by date.
"""

from datetime import date, datetime, timedelta

from airflow.decorators import dag, task
from airflow.models import Param
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.timetables.trigger import CronTriggerTimetable

from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import get_dag_param, push_dag_downstream, pull_dag_upstream
from dags.operators.DagBatchPipelineOperator import NOTICE_IDS_KEY, TriggerNoticeBatchPipelineOperator
from dags.pipelines.notice_fetcher_pipelines import notice_fetcher_by_date_pipeline
from ted_sws.event_manager.adapters.event_log_decorator import event_log
from ted_sws.event_manager.model.event_message import TechnicalEventMessage, EventMessageMetadata, \
    EventMessageProcessType
from ted_sws.event_manager.services.log import log_error

DAG_NAME = "fetch_notices_by_date"
BATCH_SIZE = 2000
FETCH_DATE_DAG_KEY = "fetch_date"
TRIGGER_COMPLETE_WORKFLOW_DAG_KEY = "trigger_complete_workflow"
TRIGGER_PARTIAL_WORKFLOW_TASK_ID = "trigger_partial_notice_proc_workflow"
TRIGGER_COMPLETE_WORKFLOW_TASK_ID = "trigger_complete_notice_proc_workflow"
CHECK_IF_TRIGGER_COMPLETE_WORKFLOW_TASK_ID = "check_if_trigger_complete_workflow"
FINISH_FETCH_BY_DATE_TASK_ID = "finish_fetch_by_date"
VALIDATE_FETCHED_NOTICES_TASK_ID = "validate_fetched_notices"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     catchup=False,
     description=__doc__[0: __doc__.find(".")],
     doc_md=__doc__,
     timetable=CronTriggerTimetable('0 1 * * *', timezone='UTC'),
     tags=['selector', 'daily-fetch'],
     params={
         FETCH_DATE_DAG_KEY: Param(
             default=f"{date.today() - timedelta(days=1)}",
             type="string",
             format="date",
             title="Date",
             description="""This field is required.
                          Date to fetch notices from TED."""
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
def fetch_notices_by_date():
    @task
    @event_log(TechnicalEventMessage(
        message="fetch_notice_from_ted",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def fetch_by_date_notice_from_ted():
        default_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        selected_date = datetime.strptime(get_dag_param(key=FETCH_DATE_DAG_KEY,
                                                        default_value=default_date), "%Y-%m-%d")
        date_wild_card = datetime.strftime(selected_date, "%Y%m%d*")
        notice_ids = notice_fetcher_by_date_pipeline(date_wild_card=date_wild_card)
        if not notice_ids:
            log_error("No notices has been fetched!")
        else:
            push_dag_downstream(key=NOTICE_IDS_KEY, value=notice_ids)

    trigger_complete_workflow = TriggerNoticeBatchPipelineOperator(task_id=TRIGGER_COMPLETE_WORKFLOW_TASK_ID,
                                                                   execute_only_one_step=False
                                                                   )
    trigger_normalisation_workflow = TriggerNoticeBatchPipelineOperator(
        task_id=TRIGGER_PARTIAL_WORKFLOW_TASK_ID,
        batch_size=BATCH_SIZE,
        execute_only_one_step=True)

    def validate_fetched_notices():
        """
        :return:
        """
        from ted_sws import config
        from ted_sws.supra_notice_manager.services.supra_notice_validator import validate_and_update_daily_supra_notice
        from datetime import datetime
        from pymongo import MongoClient
        default_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        publication_date = datetime.strptime(get_dag_param(key=FETCH_DATE_DAG_KEY,
                                                           default_value=default_date
                                                           ), "%Y-%m-%d")
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        validate_and_update_daily_supra_notice(ted_publication_date=publication_date, mongodb_client=mongodb_client)

    def _branch_selector():
        notice_ids = pull_dag_upstream(key=NOTICE_IDS_KEY)
        if not notice_ids:
            return [FINISH_FETCH_BY_DATE_TASK_ID]

        trigger_complete_workflow = get_dag_param(key=TRIGGER_COMPLETE_WORKFLOW_DAG_KEY,
                                                  default_value=True)
        push_dag_downstream(key=NOTICE_IDS_KEY, value=notice_ids)
        if trigger_complete_workflow:
            return [TRIGGER_COMPLETE_WORKFLOW_TASK_ID]
        return [TRIGGER_PARTIAL_WORKFLOW_TASK_ID]

    branch_task = BranchPythonOperator(
        task_id=CHECK_IF_TRIGGER_COMPLETE_WORKFLOW_TASK_ID,
        python_callable=_branch_selector,
    )

    validate_fetched_notices_step = PythonOperator(
        task_id=VALIDATE_FETCHED_NOTICES_TASK_ID,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
        python_callable=validate_fetched_notices
    )

    finish_step = EmptyOperator(task_id=FINISH_FETCH_BY_DATE_TASK_ID,
                                trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)

    fetch_by_date_notice_from_ted() >> branch_task >> [trigger_normalisation_workflow,
                                                       trigger_complete_workflow] >> validate_fetched_notices_step >> finish_step

    branch_task >> finish_step


dag = fetch_notices_by_date()
