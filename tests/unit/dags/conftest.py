# import os
#
# import pytest
#
# from airflow.models import DagBag
# from airflow.utils import db
# import logging

from tests import TESTS_PATH

AIRFLOW_DAG_FOLDER = TESTS_PATH.parent.resolve() / "dags"


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
