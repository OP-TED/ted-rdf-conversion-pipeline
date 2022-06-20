from pymongo import MongoClient

from dags.load_mapping_suite_in_mongodb import TRIGGER_DOCUMENT_PROC_PIPELINE_TASK_ID, \
    FETCH_MAPPING_SUITE_PACKAGE_FROM_GITHUB_INTO_MONGODB, MAPPING_SUITE_PACKAGE_NAME_DAG_PARAM_KEY
from ted_sws import config
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryMongoDB
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from tests.unit.dags import run_task

MAPPING_SUITE_ID = "package_F03_test"


def test_loading_mapping_suite_in_mongodb(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="load_mapping_suite_in_mongodb")
    worker_dag = dag_bag.get_dag(dag_id="worker_single_notice_process_orchestrator")
    assert dag is not None
    assert worker_dag is not None
    mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
    mongodb_client.drop_database(config.MONGO_DB_AGGREGATES_DATABASE_NAME)
    assert dag.has_task(FETCH_MAPPING_SUITE_PACKAGE_FROM_GITHUB_INTO_MONGODB)
    fetch_step = dag.get_task(FETCH_MAPPING_SUITE_PACKAGE_FROM_GITHUB_INTO_MONGODB)
    assert fetch_step
    mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_suite = mapping_suite_repository.get(reference=MAPPING_SUITE_ID)
    assert mapping_suite is None
    task_instance = run_task(dag=dag, task=fetch_step,
                             conf={MAPPING_SUITE_PACKAGE_NAME_DAG_PARAM_KEY: MAPPING_SUITE_ID, "load_test_data": True})
    mapping_suite = mapping_suite_repository.get(reference=MAPPING_SUITE_ID)
    assert mapping_suite is not None
    assert task_instance.state == "success"

    # trigger_step = dag.get_task(TRIGGER_DOCUMENT_PROC_PIPELINE_TASK_ID)
    # assert trigger_step
    #
    # notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    #
    # number_of_raw_notices_before_processing = len(list(notice_repository.get_notice_by_status(notice_status=NoticeStatus.RAW)))
    # print(number_of_raw_notices_before_processing)
    # assert number_of_raw_notices_before_processing != 0
    # task_instance = run_task(dag=dag, task=trigger_step,
    #                          conf={MAPPING_SUITE_PACKAGE_NAME_DAG_PARAM_KEY: MAPPING_SUITE_ID, "load_test_data": True})
    # print(task_instance)
    # #assert task_instance.state == "success"
    # number_of_raw_notices_after_processing = len(
    #     list(notice_repository.get_notice_by_status(notice_status=NoticeStatus.RAW)))
    # assert number_of_raw_notices_after_processing != number_of_raw_notices_before_processing
    # assert number_of_raw_notices_after_processing == 0

    #mongodb_client.drop_database(config.MONGO_DB_AGGREGATES_DATABASE_NAME)
