from airflow.decorators import dag, task
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import get_current_context, BranchPythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.trigger_rule import TriggerRule
from pymongo import MongoClient

from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import push_dag_downstream, pull_dag_upstream, get_dag_param
from dags.operators.DagBatchPipelineOperator import NOTICE_IDS_KEY, TriggerNoticeBatchPipelineOperator
from ted_sws import config
from ted_sws.event_manager.adapters.event_log_decorator import event_log
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.model.event_message import MappingSuiteEventMessage
from ted_sws.event_manager.services.logger_from_context import get_logger_from_dag_context, \
    handle_event_message_metadata_dag_context
from ted_sws.mapping_suite_processor.services.conceptual_mapping_processor import \
    mapping_suite_processor_from_github_expand_and_load_package_in_mongo_db

FETCH_MAPPING_SUITE_PACKAGE_FROM_GITHUB_INTO_MONGODB = "fetch_mapping_suite_package_from_github_into_mongodb"

MAPPING_SUITE_PACKAGE_NAME_DAG_PARAM_KEY = 'mapping_suite_package_name'
LOAD_TEST_DATA_DAG_PARAM_KEY = 'load_test_data'
BRANCH_OR_TAG_NAME_DAG_PARAM_KEY = "branch_or_tag_name"
GITHUB_REPOSITORY_URL_DAG_PARAM_KEY = "github_repository_url"

TRIGGER_DOCUMENT_PROC_PIPELINE_TASK_ID = "trigger_document_proc_pipeline"
FINISH_LOADING_MAPPING_SUITE_TASK_ID = "finish_loading_mapping_suite"
CHECK_IF_LOAD_TEST_DATA_TASK_ID = "check_if_load_test_data"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     tags=['fetch', 'mapping-suite', 'github'])
def load_mapping_suite_in_mongodb():
    @task
    @event_log(is_loggable=False)
    def fetch_mapping_suite_package_from_github_into_mongodb(**context_args):
        """

        :return:
        """
        event_logger: EventLogger = get_logger_from_dag_context(context_args)
        event_message = MappingSuiteEventMessage()
        event_message.start_record()
        context = get_current_context()

        load_test_data = get_dag_param(key=LOAD_TEST_DATA_DAG_PARAM_KEY, default_value=False)
        mapping_suite_package_name = get_dag_param(key=MAPPING_SUITE_PACKAGE_NAME_DAG_PARAM_KEY)
        branch_or_tag_name = get_dag_param(key=BRANCH_OR_TAG_NAME_DAG_PARAM_KEY)
        github_repository_url = get_dag_param(key=GITHUB_REPOSITORY_URL_DAG_PARAM_KEY)

        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_ids = mapping_suite_processor_from_github_expand_and_load_package_in_mongo_db(
            mongodb_client=mongodb_client,
            mapping_suite_package_name=mapping_suite_package_name,
            load_test_data=load_test_data,
            branch_or_tag_name=branch_or_tag_name,
            github_repository_url=github_repository_url
        )
        notice_ids = list(set(notice_ids))
        if load_test_data:
            push_dag_downstream(key=NOTICE_IDS_KEY, value=notice_ids)
        handle_event_message_metadata_dag_context(event_message, context)
        if mapping_suite_package_name:
            event_message.mapping_suite_id = mapping_suite_package_name
        event_message.end_record()
        event_logger.info(event_message)

    def _branch_selector():
        load_test_data = get_dag_param(key=LOAD_TEST_DATA_DAG_PARAM_KEY, default_value=False)
        if load_test_data:
            push_dag_downstream(key=NOTICE_IDS_KEY, value=pull_dag_upstream(key=NOTICE_IDS_KEY))
            return [TRIGGER_DOCUMENT_PROC_PIPELINE_TASK_ID]
        return [FINISH_LOADING_MAPPING_SUITE_TASK_ID]

    branch_task = BranchPythonOperator(
        task_id=CHECK_IF_LOAD_TEST_DATA_TASK_ID,
        python_callable=_branch_selector,
    )
    finish_step = DummyOperator(task_id=FINISH_LOADING_MAPPING_SUITE_TASK_ID,
                                trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)

    trigger_document_proc_pipeline = TriggerNoticeBatchPipelineOperator(task_id=TRIGGER_DOCUMENT_PROC_PIPELINE_TASK_ID)
    fetch_mapping_suite_package_from_github_into_mongodb() >> branch_task
    trigger_document_proc_pipeline >> finish_step
    branch_task >> [trigger_document_proc_pipeline, finish_step]


dag = load_mapping_suite_in_mongodb()
