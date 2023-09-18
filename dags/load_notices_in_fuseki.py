"""
This DAG is used to load notices in Fuseki.
"""

from airflow.decorators import dag, task
from airflow.models import Param
from pymongo import MongoClient

from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import get_dag_param
from ted_sws import config
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_manager.adapters.triple_store import FusekiAdapter
from ted_sws.notice_publisher_triple_store.services.load_transformed_notice_into_triple_store import \
    load_rdf_manifestation_into_triple_store

FUSEKI_DATASET_NAME_DAG_PARAM_KEY = "fuseki_dataset_name"
NOTICE_STATUS_DAG_PARAM_KEY = "notice_status"
DEFAULT_FUSEKI_DATASET_NAME = "mdr_dataset"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     tags=['load', 'notices', 'fuseki'],
     description=__doc__[0: __doc__.find(".")],
     doc_md=__doc__,
     params={
            FUSEKI_DATASET_NAME_DAG_PARAM_KEY: Param(
                default=DEFAULT_FUSEKI_DATASET_NAME,
                type="string",
                title="Fuseki dataset name",
                description="This field is used to specify the name of the dataset in Fuseki."
            ),
            NOTICE_STATUS_DAG_PARAM_KEY: Param(
                default=str(NoticeStatus.PUBLISHED),
                type="string",
                title="Notice status",
                description="This field is used to filter notices by status."
            )
     }
     )
def load_notices_in_fuseki():
    @task
    def load_distilled_rdf_manifestations_in_fuseki():
        """

        :return:
        """
        fuseki_dataset_name = get_dag_param(key=FUSEKI_DATASET_NAME_DAG_PARAM_KEY,
                                            default_value=DEFAULT_FUSEKI_DATASET_NAME)
        notice_status = get_dag_param(key=NOTICE_STATUS_DAG_PARAM_KEY, default_value=str(NoticeStatus.PUBLISHED))
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        fuseki_repository = FusekiAdapter()
        notices = notice_repository.get_notices_by_status(notice_status=NoticeStatus[notice_status])
        for notice in notices:
            load_rdf_manifestation_into_triple_store(rdf_manifestation=notice.distilled_rdf_manifestation,
                                                     triple_store_repository=fuseki_repository,
                                                     repository_name=fuseki_dataset_name)

    load_distilled_rdf_manifestations_in_fuseki()


dag = load_notices_in_fuseki()
