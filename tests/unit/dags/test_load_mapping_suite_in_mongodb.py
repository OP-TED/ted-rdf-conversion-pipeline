FETCH_MAPPING_SUITE_PACKAGE_FROM_GITHUB_INTO_MONGODB = "fetch_mapping_suite_package_from_github_into_mongodb"


def test_selector_daily_fetch_orchestrator(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="load_mapping_suite_in_mongodb")
    assert dag is not None
    assert dag.has_task(FETCH_MAPPING_SUITE_PACKAGE_FROM_GITHUB_INTO_MONGODB)
