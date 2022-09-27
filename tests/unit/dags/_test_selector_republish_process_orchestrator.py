SELECT_NOTICES_FOR_RE_PUBLISH_AND_RESET_STATUS_TASK_ID = "select_notices_for_re_publish_and_reset_status"
TRIGGER_WORKER_FOR_PUBLISH_BRANCH_TASK_ID = "trigger_worker_for_publish_branch"


def test_selector_republish_process_orchestrator(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="selector_re_publish_process_orchestrator")
    assert dag is not None
    assert dag.has_task(SELECT_NOTICES_FOR_RE_PUBLISH_AND_RESET_STATUS_TASK_ID)
    assert dag.has_task(TRIGGER_WORKER_FOR_PUBLISH_BRANCH_TASK_ID)
    select_notices_for_re_publish_and_reset_status_task = dag.get_task(
        SELECT_NOTICES_FOR_RE_PUBLISH_AND_RESET_STATUS_TASK_ID)
    trigger_worker_for_publish_branch_task = dag.get_task(TRIGGER_WORKER_FOR_PUBLISH_BRANCH_TASK_ID)
    assert select_notices_for_re_publish_and_reset_status_task
    assert trigger_worker_for_publish_branch_task
    assert TRIGGER_WORKER_FOR_PUBLISH_BRANCH_TASK_ID in set(
        map(lambda task: task.task_id, select_notices_for_re_publish_and_reset_status_task.downstream_list))
    assert SELECT_NOTICES_FOR_RE_PUBLISH_AND_RESET_STATUS_TASK_ID in set(
        map(lambda task: task.task_id, trigger_worker_for_publish_branch_task.upstream_list))
