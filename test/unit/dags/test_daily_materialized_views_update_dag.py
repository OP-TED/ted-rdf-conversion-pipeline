from airflow.models import DagBag


def test_daily_materialized_views_update_dag_loaded(dag_bag: DagBag, daily_materialised_views_dag_id: str):
    assert daily_materialised_views_dag_id in dag_bag.dags
    dag = dag_bag.dags[daily_materialised_views_dag_id]
    assert dag is not None


def test_daily_materialized_views_update_dag_structure(dag_bag: DagBag, daily_materialised_views_dag_id: str):
    dag = dag_bag.dags[daily_materialised_views_dag_id]

    task_ids = [task.task_id for task in dag.tasks]
    expected_tasks = [
        "create_materialised_view",
        "create_kpi_collection_for_notices",
        "aggregate_batch_logs"
    ]
    for task_id in expected_tasks:
        assert task_id in task_ids

    assert len(dag.tasks) == 3

    create_view_task = dag.get_task("create_materialised_view")
    kpi_collection_task = dag.get_task("create_kpi_collection_for_notices")
    aggregate_logs_task = dag.get_task("aggregate_batch_logs")

    assert kpi_collection_task.task_id in [task.task_id for task in create_view_task.downstream_list]
    assert aggregate_logs_task.task_id in [task.task_id for task in kpi_collection_task.downstream_list]

    assert create_view_task.task_id in [task.task_id for task in kpi_collection_task.upstream_list]
    assert kpi_collection_task.task_id in [task.task_id for task in aggregate_logs_task.upstream_list]


def test_daily_materialized_views_update_dag_default_args(dag_bag: DagBag, daily_materialised_views_dag_id: str):
    assert daily_materialised_views_dag_id in dag_bag.dags
    dag = dag_bag.dags[daily_materialised_views_dag_id]

    assert dag.max_active_runs == 1
    assert not dag.catchup
    assert "mongodb" in dag.tags
    assert "daily-views-update" in dag.tags
