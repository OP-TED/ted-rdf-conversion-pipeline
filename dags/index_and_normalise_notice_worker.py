from pymongo import MongoClient

from dags.dags_utils import pull_dag_upstream, push_dag_downstream
from ted_sws import config

from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_sampler.services.notice_xml_indexer import index_notice
from ted_sws.metadata_normaliser.services.metadata_normalizer import normalise_notice_by_id

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context

from dags import DEFAULT_DAG_ARGUMENTS

NOTICE_ID = "notice_id"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     tags=['worker', 'index_and_normalise_notice'])
def index_and_normalise_notice_worker():
    """

    :return:
    """

    @task
    def index_notice():
        """

        :return:
        """
        context = get_current_context()
        dag_params = context["dag_run"].conf
        notice_id = dag_params["notice_id"]
        push_dag_downstream(key=NOTICE_ID, value=notice_id)
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        notice = notice_repository.get(reference=notice_id)
        indexed_notice = index_notice(notice=notice)
        notice_repository.update(notice=indexed_notice)

    @task
    def normalise_notice_metadata():
        """

        :return:
        """
        notice_id = pull_dag_upstream(NOTICE_ID)
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        normalised_notice = normalise_notice_by_id(notice_id=notice_id, notice_repository=notice_repository)
        notice_repository.update(notice=normalised_notice)

    index_notice() >> normalise_notice_metadata()


dag = index_and_normalise_notice_worker()
