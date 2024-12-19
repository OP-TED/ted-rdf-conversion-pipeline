import logging
import os

from airflow.exceptions import AirflowTimetableInvalid
from airflow.models import DagBag
from airflow.timetables.trigger import CronTriggerTimetable
from airflow.utils import db
from psutil.tests import pytest

from dags.fetch_notices_by_date import FETCHER_DAG_NAME
from tests import TESTS_PATH

AIRFLOW_DAG_FOLDER = TESTS_PATH.parent.resolve() / "dags"


@pytest.fixture()
def dag_bag():
    os.environ["AIRFLOW_HOME"] = str(AIRFLOW_DAG_FOLDER)
    os.environ["AIRFLOW__CORE__LOAD_EXAMPLES"] = "False"
    # Initialising the Airflow DB so that it works properly with the new AIRFLOW_HOME
    logging.disable(logging.CRITICAL)
    db.resetdb()
    db.initdb()
    logging.disable(logging.NOTSET)
    dag_bag = DagBag(dag_folder=AIRFLOW_DAG_FOLDER, include_examples=False,
                     read_dags_from_db=False)
    return dag_bag


# @pytest.fixture
# def dag_bag():
#     return DagBag(dag_folder=AIRFLOW_DAG_FOLDER, include_examples=False, read_dags_from_db=False)


@pytest.fixture
def fetcher_dag_id():
    return FETCHER_DAG_NAME


@pytest.fixture
def example_cron_table() -> str:
    return "15 14 1 * *"


@pytest.fixture
def example_wrong_cron_table() -> str:
    return "1234"


@pytest.fixture
def example_dag_cron_table(example_cron_table) -> CronTriggerTimetable:
    return CronTriggerTimetable(cron=example_cron_table, timezone="UTC")


@pytest.fixture
def airflow_timetable_import_error_name() -> str:
    return AirflowTimetableInvalid.__name__



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
