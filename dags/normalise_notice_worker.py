from airflow.utils.trigger_rule import TriggerRule
from pymongo import MongoClient

from dags.dags_utils import pull_dag_upstream, push_dag_downstream
from ted_sws import config

from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.metadata_normaliser.services.metadata_normalizer import normalise_notice_by_id

from airflow.decorators import dag
from airflow.operators.python import get_current_context, PythonOperator

from dags import DEFAULT_DAG_ARGUMENTS

NOTICE_ID = "notice_id"
MAPPING_SUITE_ID = "mapping_suite_id"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     tags=['worker', 'normalise'])
def normalise_worker():
    """

    :return:
    """

    def _normalise_notice_metadata():
        """

        :return:
        """
        notice_id = pull_dag_upstream(NOTICE_ID)
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        normalised_notice = normalise_notice_by_id(notice_id=notice_id, notice_repository=notice_repository)
        notice_repository.update(notice=normalised_notice)

    normalise_notice_metadata = PythonOperator(
        task_id="normalise_notice_metadata",
        python_callable=_normalise_notice_metadata,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS
    )

    def get_config():
        context = get_current_context()
        dag_params = context["dag_run"].conf
        push_dag_downstream(key=NOTICE_ID, value=dag_params["notice_id"])

    get_config_task = PythonOperator(
        task_id='start_processing_notice',
        python_callable=get_config,
    )

    get_config_task >> normalise_notice_metadata


dag = normalise_worker()
