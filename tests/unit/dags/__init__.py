from datetime import timezone
from typing import List

from airflow.models import DagRun, TaskInstance
from airflow.utils.types import DagRunType


def run_task(dag, task, conf: dict, ignore_first_depends_on_past=True) -> TaskInstance:
    start_date = dag.default_args["start_date"]
    end_date = dag.default_args["start_date"]
    start_date = start_date or task.start_date
    end_date = end_date or task.end_date or timezone.utcnow()

    info = list(task.dag.iter_dagrun_infos_between(start_date, end_date, align=False))[0]
    ignore_depends_on_past = info.logical_date == start_date and ignore_first_depends_on_past
    dr = DagRun(
        dag_id=task.dag_id,
        run_id=DagRun.generate_run_id(DagRunType.MANUAL, info.logical_date),
        run_type=DagRunType.MANUAL,
        execution_date=info.logical_date,
        data_interval=info.data_interval,
        conf=conf
    )
    ti = TaskInstance(task, run_id=None)
    ti.dag_run = dr
    ti.run(
        mark_success=False,
        ignore_task_deps=True,
        ignore_depends_on_past=ignore_depends_on_past,
        ignore_ti_state=False,
        test_mode=True,
    )
    return ti