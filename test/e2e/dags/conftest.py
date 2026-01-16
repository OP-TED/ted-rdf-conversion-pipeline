import pytest

# from airflow.models import DagBag
# from airflow.utils import db
# import logging
from src.ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from src.ted_sws.mapping_suite_processor.services.mapping_package_processor import \
    mapping_package_processor_from_github_expand_and_load_package_in_mongo_db
from test import TESTS_PATH

AIRFLOW_DAG_FOLDER = TESTS_PATH.parent.resolve() / "dags"

MAPPING_PACKAGE_ID = "package_F03_test"
MAPPING_PACKAGE_ID_WITH_VERSION = "package_F03_test_v2.3.0"

#
# @pytest.fixture(scope="session")
# def dag_bag():
#     os.environ["AIRFLOW_HOME"] = str(AIRFLOW_DAG_FOLDER)
#     os.environ["AIRFLOW__CORE__LOAD_EXAMPLES"] = "False"
#     # Initialising the Airflow DB so that it works properly with the new AIRFLOW_HOME
#     logging.disable(logging.CRITICAL)
#     db.resetdb()
#     db.initdb()
#     logging.disable(logging.NOTSET)
#     dag_bag = DagBag(dag_folder=AIRFLOW_DAG_FOLDER, include_examples=False,
#                      read_dags_from_db=False)
#     return dag_bag


@pytest.fixture
def mapping_package_id():
    return MAPPING_PACKAGE_ID


@pytest.fixture
def mapping_package_id_with_version():
    return MAPPING_PACKAGE_ID_WITH_VERSION


@pytest.fixture
def notice_repository(mongodb_client, mapping_package_id):
    mapping_package_processor_from_github_expand_and_load_package_in_mongo_db(
        mapping_package_name=mapping_package_id,
        mongodb_client=mongodb_client,
        load_test_data=True
    )
    return NoticeRepository(mongodb_client=mongodb_client)
