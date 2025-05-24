import os
import tempfile

import pytest
from airflow.models import DagBag, Variable
from airflow.timetables.trigger import CronTriggerTimetable
from airflow.utils.db import resetdb, initdb

from dags.daily_materialized_views_update import DAILY_MATERIALISED_VIEWS_DAG_NAME
from dags.fetch_notices_by_date import FETCHER_DAG_NAME
from tests import AIRFLOW_DAG_FOLDER


@pytest.fixture(scope="session", autouse=True)
def setup_airflow_for_all_tests():
    """Setup Airflow DB once at the beginning of the test session"""
    temp_db_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".db")
    os.environ["AIRFLOW__CORE__SQL_ALCHEMY_CONN"] = f"sqlite:///{temp_db_file.name}"
    os.environ["AIRFLOW__CORE__LOAD_EXAMPLES"] = "False"
    os.environ["AIRFLOW__CORE__UNIT_TEST_MODE"] = "True"
    resetdb()  # Reset the database first to ensure clean state
    initdb()
    yield
    # Cleanup after all tests complete
    if os.path.exists(temp_db_file.name):
        temp_db_file.close()


@pytest.fixture(scope="function")
def setup_airflow():
    """This fixture now just makes sure the DB is clean for each test,
    but doesn't reinitialize the connection"""
    resetdb()
    initdb()


@pytest.fixture
def dag_bag(dag_materialised_view_update_schedule_variable_name,
            dag_fetch_schedule_variable_name,
            setup_airflow) -> DagBag:
    Variable.delete(key=dag_materialised_view_update_schedule_variable_name)
    Variable.delete(key=dag_fetch_schedule_variable_name)
    return DagBag(
        dag_folder=AIRFLOW_DAG_FOLDER,
        include_examples=False,  # Same as: os.environ["AIRFLOW__CORE__LOAD_EXAMPLES"] = "False"
        read_dags_from_db=False,
        collect_dags=True)


@pytest.fixture
def fetcher_dag_name() -> str:
    return FETCHER_DAG_NAME


@pytest.fixture
def daily_materialised_views_dag_id() -> str:
    return DAILY_MATERIALISED_VIEWS_DAG_NAME


@pytest.fixture
def example_cron_table() -> str:
    return "15 14 1 * *"


@pytest.fixture
def example_wrong_cron_table() -> str:
    return "wrong_cron"


@pytest.fixture
def example_dag_cron_table(example_cron_table) -> CronTriggerTimetable:
    return CronTriggerTimetable(cron=example_cron_table, timezone="UTC")


@pytest.fixture
def airflow_timetable_import_error_message() -> str:
    return "FormatException"


@pytest.fixture
def dag_fetch_schedule_variable_name() -> str:
    """
    According to MM of meeting with OP from 2024.12.28
    """
    return "SCHEDULE_DAG_FETCH"


@pytest.fixture
def dag_materialised_view_update_schedule_variable_name() -> str:
    """
    According to MM of meeting with OP from 2024.12.28
    """
    return "SCHEDULE_DAG_MATERIALIZED_VIEW_UPDATE"
