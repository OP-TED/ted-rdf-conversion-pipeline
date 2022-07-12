from airflow.decorators import dag, task
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import get_current_context, BranchPythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.trigger_rule import TriggerRule
from pymongo import MongoClient

from dags import DEFAULT_DAG_ARGUMENTS
from ted_sws import config
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
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
TRIGGER_DOCUMENT_PROC_PIPELINE_TASK_ID = "trigger_document_proc_pipeline"
FINISH_LOADING_MAPPING_SUITE_TASK_ID = "finish_loading_mapping_suite"
CHECK_IF_LOAD_TEST_DATA_TASK_ID = "check_if_load_test_data"

DAG_NAME = "load_mapping_suite_in_mongodb"


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
        event_message = MappingSuiteEventMessage(name=DAG_NAME)
        event_message.start_record()

        context = get_current_context()
        dag_conf = context["dag_run"].conf

        handle_event_message_metadata_dag_context(event_message, DAG_NAME, context)
        if MAPPING_SUITE_PACKAGE_NAME_DAG_PARAM_KEY in dag_conf.keys():
            event_message.mapping_suite_id = dag_conf[MAPPING_SUITE_PACKAGE_NAME_DAG_PARAM_KEY]

        key = MAPPING_SUITE_PACKAGE_NAME_DAG_PARAM_KEY
        load_test_data = dag_conf[
            LOAD_TEST_DATA_DAG_PARAM_KEY] if LOAD_TEST_DATA_DAG_PARAM_KEY in dag_conf.keys() else False
        if key in dag_conf.keys():
            mapping_suite_package_name = dag_conf[key]
            mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
            mapping_suite_processor_from_github_expand_and_load_package_in_mongo_db(
                mapping_suite_package_name=mapping_suite_package_name,
                mongodb_client=mongodb_client,
                load_test_data=load_test_data
            )
        else:
            raise KeyError(f"The key={key} is not present in context")

        event_message.end_record()
        event_logger.info(event_message)

    @task
    @event_log(is_loggable=False)
    def trigger_document_proc_pipeline(**context_args):
        event_logger: EventLogger = get_logger_from_dag_context(context_args)
        event_message = MappingSuiteEventMessage(name=DAG_NAME)
        event_message.start_record()

        context = get_current_context()
        dag_conf = context["dag_run"].conf

        handle_event_message_metadata_dag_context(event_message, DAG_NAME, context)
        if MAPPING_SUITE_PACKAGE_NAME_DAG_PARAM_KEY in dag_conf.keys():
            event_message.mapping_suite_id = dag_conf[MAPPING_SUITE_PACKAGE_NAME_DAG_PARAM_KEY]

        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        notices = notice_repository.get_notice_by_status(notice_status=NoticeStatus.RAW)
        for notice in notices:
            TriggerDagRunOperator(
                task_id=f'trigger_worker_dag_{notice.ted_id}',
                trigger_dag_id="worker_single_notice_process_orchestrator",
                conf={"notice_id": notice.ted_id,
                      "notice_status": str(notice.status)
                      }
            ).execute(context=context)

        event_message.end_record()
        event_logger.info(event_message)

    def _get_task_run():
        context = get_current_context()
        dag_conf = context["dag_run"].conf
        load_test_data = dag_conf[
            LOAD_TEST_DATA_DAG_PARAM_KEY] if LOAD_TEST_DATA_DAG_PARAM_KEY in dag_conf.keys() else False
        if load_test_data:
            return [TRIGGER_DOCUMENT_PROC_PIPELINE_TASK_ID]
        return [FINISH_LOADING_MAPPING_SUITE_TASK_ID]

    branch_task = BranchPythonOperator(
        task_id=CHECK_IF_LOAD_TEST_DATA_TASK_ID,
        python_callable=_get_task_run,
    )
    finish_step = DummyOperator(task_id=FINISH_LOADING_MAPPING_SUITE_TASK_ID,
                                trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)

    trigger_document_proc_pipeline_executor = trigger_document_proc_pipeline()
    fetch_mapping_suite_package_from_github_into_mongodb() >> branch_task
    trigger_document_proc_pipeline_executor >> finish_step
    branch_task >> [trigger_document_proc_pipeline_executor, finish_step]


dag = load_mapping_suite_in_mongodb()
