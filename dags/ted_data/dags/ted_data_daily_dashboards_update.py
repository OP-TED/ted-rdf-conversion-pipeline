from pathlib import Path

from airflow.decorators import dag, task
from pymongo import MongoClient

from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import get_dag_param
from dags.pipelines.notice_selectors_pipelines import notice_ids_selector_by_status
from ted_sws import config
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_manager.adapters.triple_store import FusekiAdapter
from ted_sws.notice_publisher_triple_store.services.load_transformed_notice_into_triple_store import \
    load_rdf_manifestation_into_triple_store

DAG_NAME = "ted_data_daily_dashboards_update"
DEFAULT_FUSEKI_DATASET_NAME = "ted_data_dataset"
FORM_NUMBER_DAG_PARAM = "form_number"
START_DATE_DAG_PARAM = "start_date"
END_DATE_DAG_PARAM = "end_date"
XSD_VERSION_DAG_PARAM = "xsd_version"
SPARQL_FILE_PREFIX = ".rq"

TED_DATA_MONGODB_DATABASE_NAME = 'ted_analytics'  # TODO: temporary while not put in config resolver
SPARQL_QUERIES_FOLDER = 'dags/resources/sparql_queries'  # TODO: temporary while not put in config resolver

LOAD_TO_FUSEKI_TARGET_NOTICE_STATES = [NoticeStatus.DISTILLED, NoticeStatus.VALIDATED, NoticeStatus.PACKAGED,
                                       NoticeStatus.PUBLISHED, NoticeStatus.ELIGIBLE_FOR_PUBLISHING,
                                       NoticeStatus.ELIGIBLE_FOR_PACKAGING, NoticeStatus.INELIGIBLE_FOR_PACKAGING,
                                       NoticeStatus.INELIGIBLE_FOR_PUBLISHING]


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     catchup=False,
     schedule_interval="0 9 * * *",
     tags=['ted-data', 'daily-dashboards-update'])
def ted_data_daily_dashboards_update():
    @task
    def load_data_to_fuseki():

        form_number = get_dag_param(key=FORM_NUMBER_DAG_PARAM)
        start_date = get_dag_param(key=START_DATE_DAG_PARAM)
        end_date = get_dag_param(key=END_DATE_DAG_PARAM)
        xsd_version = get_dag_param(key=XSD_VERSION_DAG_PARAM)

        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        fuseki_repository = FusekiAdapter()
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        notice_ids = notice_ids_selector_by_status(notice_statuses=LOAD_TO_FUSEKI_TARGET_NOTICE_STATES,
                                                   form_number=form_number, start_date=start_date,
                                                   end_date=end_date, xsd_version=xsd_version)
        for notice_id in notice_ids:
            notice = notice_repository.get(reference=notice_id)
            if notice is not None:
                load_rdf_manifestation_into_triple_store(rdf_manifestation=notice.distilled_rdf_manifestation,
                                                         triple_store_repository=fuseki_repository,
                                                         repository_name=DEFAULT_FUSEKI_DATASET_NAME)

    @task
    def execute_sparql_queries_and_store_into_mongo_db():
        """

        :return:
        """
        fuseki_adapter = FusekiAdapter()
        fuseki_endpoint = fuseki_adapter.get_sparql_triple_store_endpoint(DEFAULT_FUSEKI_DATASET_NAME)
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        mongodb_database = mongodb_client[TED_DATA_MONGODB_DATABASE_NAME]
        queries_path = Path(SPARQL_QUERIES_FOLDER)
        for sparql_file_path in queries_path.rglob(f"*{SPARQL_FILE_PREFIX}"):
            query_result = fuseki_endpoint.with_query_from_file(str(sparql_file_path)).fetch_tree()
            query_collection = mongodb_database[sparql_file_path.stem]
            query_collection.insert_one(query_result)

    load_data_to_fuseki() >> execute_sparql_queries_and_store_into_mongo_db()


dag = ted_data_daily_dashboards_update()
