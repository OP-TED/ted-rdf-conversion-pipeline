import pytest

from airflow.models import DagBag


@pytest.fixture()
def dag_bag():
    return DagBag()