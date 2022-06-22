from pymongo import MongoClient

from ted_sws import config
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from tests.unit.dags import run_task, FULL_BRANCH_TASK_IDS

START_PROCESSING_NOTICE_TASK_ID = "start_processing_notice"
NORMALISE_NOTICE_METADATA_TASK_ID = "normalise_notice_metadata"
_check_eligibility_for_transformation = "check_eligibility_for_transformation"
NOTICE_ID = "000055-2020"
DAG_CONFIG = {"notice_id": NOTICE_ID, "notice_status": "RAW"}
XCOM_DEFAULT = {"notice_id": NOTICE_ID}
#XCOM_MAPPING_SU


def execute_dag_step(dag, task_id: str, xcom_push_data: dict = None):
    assert dag.has_task(task_id)
    task = dag.get_task(task_id)
    assert task
    task_instance = run_task(dag, task, conf=DAG_CONFIG, xcom_push_data=xcom_push_data)
    assert task_instance.state == "success"


def check_notice_status(notice_repository: NoticeRepository, notice_status: NoticeStatus):
    notice = notice_repository.get(reference=NOTICE_ID)
    assert notice.status == notice_status


def test_worker_dag_steps(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="worker_single_notice_process_orchestrator")
    assert dag is not None
    mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    check_notice_status(notice_repository=notice_repository, notice_status=NoticeStatus.RAW)
    execute_dag_step(dag, task_id=START_PROCESSING_NOTICE_TASK_ID)
    execute_dag_step(dag, task_id=NORMALISE_NOTICE_METADATA_TASK_ID, xcom_push_data=XCOM_DEFAULT)
    check_notice_status(notice_repository=notice_repository, notice_status=NoticeStatus.NORMALISED_METADATA)
