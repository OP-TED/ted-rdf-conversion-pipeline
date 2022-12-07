from datetime import timedelta

from airflow.decorators import dag, task
from airflow.operators.dummy import DummyOperator
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

DAG_NAME = "notice_fetch_by_date_workflow"
BATCH_SIZE = 2000
WILD_CARD_DAG_KEY = "wild_card"
TRIGGER_COMPLETE_WORKFLOW_DAG_KEY = "trigger_complete_workflow"
TRIGGER_PARTIAL_WORKFLOW_TASK_ID = "trigger_partial_notice_proc_workflow"
TRIGGER_COMPLETE_WORKFLOW_TASK_ID = "trigger_complete_notice_proc_workflow"
CHECK_IF_TRIGGER_COMPLETE_WORKFLOW_TASK_ID = "check_if_trigger_complete_workflow"
FINISH_FETCH_BY_DATE_TASK_ID = "finish_fetch_by_date"
VALIDATE_FETCHED_NOTICES_TASK_ID = "validate_fetched_notices"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     catchup=False,
     timetable=CronTriggerTimetable('0 1 * * *', timezone='UTC'),
     tags=['selector', 'daily-fetch'])
def notice_fetch_by_date_workflow():
    @task
    @event_log(TechnicalEventMessage(
        message="fetch_notice_from_ted",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def fetch_by_date_notice_from_ted():
        notice_ids = notice_fetcher_by_date_pipeline(date_wild_card=get_dag_param(key=WILD_CARD_DAG_KEY))
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

    def validate_fetched_notices():
        """
        :return:
        """
        from ted_sws import config
        from ted_sws.supra_notice_manager.services.supra_notice_validator import validate_and_update_daily_supra_notice
        from datetime import datetime
        from pymongo import MongoClient

        publication_date = datetime.strptime(get_dag_param(key=WILD_CARD_DAG_KEY,
                                                           default_value=(datetime.now() - timedelta(days=1)).strftime(
                                                               "%Y%m%d*")), "%Y%m%d*")
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        validate_and_update_daily_supra_notice(notice_publication_day=publication_date,
                                               mongodb_client=mongodb_client)

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

    validate_fetched_notices_step = PythonOperator(
        task_id=VALIDATE_FETCHED_NOTICES_TASK_ID,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
        python_callable=validate_fetched_notices
    )

    finish_step = DummyOperator(task_id=FINISH_FETCH_BY_DATE_TASK_ID,
                                trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)

    fetch_by_date_notice_from_ted() >> branch_task >> [trigger_normalisation_workflow,
                                                       trigger_complete_workflow] >> validate_fetched_notices_step >> finish_step


dag = notice_fetch_by_date_workflow()
