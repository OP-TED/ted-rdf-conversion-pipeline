from airflow.utils.context import Context


class FakeDAG:
    dag_id: str = "FAKE_DAG_ID"


class FakeDAGRun:
    run_id: str = "FAKE_RUN_ID"


class FakeTask:
    task_id: str = "FAKE_TASK_ID"


class FakeDAGContext(Context):
    def __init__(self):
        super().__init__({
            "dag": FakeDAG(),
            "dag_run": FakeDAGRun(),
            "task": FakeTask(),
            "params": {}
        })
