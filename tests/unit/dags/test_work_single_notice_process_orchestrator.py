from tests.unit.dags import TRANSFORM_BRANCH_TASK_IDS, PACKAGE_BRANCH_TASK_IDS, PUBLISH_BRANCH_TASK_IDS, \
    FULL_BRANCH_TASK_IDS


def _test_dag_branch(dag, task_ids: list):
    for task_id in task_ids:
        assert dag.has_task(task_id)
    for index in range(0, len(task_ids) - 1):
        task_a = dag.get_task(task_ids[index])
        task_b = dag.get_task(task_ids[index + 1])
        assert task_b.task_id in set(map(lambda task: task.task_id, task_a.downstream_list))
        assert task_a.task_id in set(
            map(lambda task: task.task_id, task_b.upstream_list))


def test_transform_branch_worker_single_notice_process_orchestrator(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="worker_single_notice_process_orchestrator")
    assert dag is not None
    _test_dag_branch(dag, TRANSFORM_BRANCH_TASK_IDS)


def test_package_branch_worker_single_notice_process_orchestrator(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="worker_single_notice_process_orchestrator")
    assert dag is not None
    _test_dag_branch(dag, PACKAGE_BRANCH_TASK_IDS)


def test_publish_branch_worker_single_notice_process_orchestrator(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="worker_single_notice_process_orchestrator")
    assert dag is not None
    _test_dag_branch(dag, PUBLISH_BRANCH_TASK_IDS)


def test_full_branch_worker_single_notice_process_orchestrator(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="worker_single_notice_process_orchestrator")
    assert dag is not None
    _test_dag_branch(dag, FULL_BRANCH_TASK_IDS)


def test_worker_single_notice_process_orchestrator(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="worker_single_notice_process_orchestrator")
    assert dag is not None
