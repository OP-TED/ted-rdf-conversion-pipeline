from airflow.models import DagBag


def test_dags_are_loaded_successfully(dag_bag: DagBag):
    assert dag_bag.import_errors == {}
    for dag in dag_bag.dags.values():
        assert dag is not None
        assert len(dag.tasks) > 0