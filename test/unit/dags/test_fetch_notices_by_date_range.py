from airflow.models import DagBag

from src.dags import RUN_MATERIALISED_VIEW_DAG_PARAM
from src.dags.fetch_notices_by_date_range import DAG_ID as DAG_NAME


def test_run_materialised_view_param_exists_in_fetch_by_date_range(dag_bag: DagBag):
    assert DAG_NAME in dag_bag.dags
    dag = dag_bag.dags[DAG_NAME]
    assert RUN_MATERIALISED_VIEW_DAG_PARAM in dag.params
