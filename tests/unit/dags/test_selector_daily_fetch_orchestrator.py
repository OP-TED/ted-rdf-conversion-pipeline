FETCH_NOTICE_FROM_TED_TASK_ID = "fetch_notice_from_ted"
TRIGGER_DOCUMENT_PROC_PIPELINE_TASK_ID = "trigger_document_proc_pipeline"


def test_selector_daily_fetch_orchestrator(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="selector_daily_fetch_orchestrator")
    assert dag is not None
    assert dag.has_task(FETCH_NOTICE_FROM_TED_TASK_ID)
    assert dag.has_task(TRIGGER_DOCUMENT_PROC_PIPELINE_TASK_ID)
    fetch_notice_from_ted_task = dag.get_task(FETCH_NOTICE_FROM_TED_TASK_ID)
    trigger_document_proc_pipeline_task = dag.get_task(TRIGGER_DOCUMENT_PROC_PIPELINE_TASK_ID)
    assert fetch_notice_from_ted_task
    assert trigger_document_proc_pipeline_task
    assert TRIGGER_DOCUMENT_PROC_PIPELINE_TASK_ID in set(
        map(lambda task: task.task_id, fetch_notice_from_ted_task.downstream_list))
    assert FETCH_NOTICE_FROM_TED_TASK_ID in set(
        map(lambda task: task.task_id, trigger_document_proc_pipeline_task.upstream_list))
