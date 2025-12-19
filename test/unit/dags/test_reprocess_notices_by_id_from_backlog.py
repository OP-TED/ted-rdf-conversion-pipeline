from airflow.models import DagBag

from src.dags import RUN_MATERIALISED_VIEW_DAG_PARAM
from src.dags.reprocess_notices_from_backlog_by_id import DAG_ID as DAG_NAME


def test_run_materialised_view_param_exists_in_reprocess_by_id(dag_bag: DagBag):
    assert DAG_NAME in dag_bag.dags
    dag = dag_bag.dags[DAG_NAME]
    assert RUN_MATERIALISED_VIEW_DAG_PARAM in dag.params
