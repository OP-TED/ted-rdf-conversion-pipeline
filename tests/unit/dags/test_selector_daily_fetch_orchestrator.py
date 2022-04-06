
def test_selector_daily_fetch_orchestrator(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="selector_daily_fetch_orchestrator")
    assert dag is not None
    print(dag.tasks)