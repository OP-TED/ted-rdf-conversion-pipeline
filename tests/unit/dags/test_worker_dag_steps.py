from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.models import DagRun, TaskInstance
from airflow.operators.python import BranchPythonOperator
from airflow.utils.state import State
from airflow.utils.types import DagRunType

START_PROCESSING_NOTICE_TASK_ID = "start_processing_notice"


def run_task(task, start_date, end_date, conf, ignore_first_depends_on_past=True):
    start_date = start_date or task.start_date
    end_date = end_date or task.end_date or timezone.utcnow()

    for info in task.dag.iter_dagrun_infos_between(start_date, end_date, align=False):
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
            ignore_depends_on_past=ignore_depends_on_past,
            ignore_ti_state=False,
            test_mode=True,
        )


def test_worker_dag_steps(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="worker_single_notice_process_orchestrator")
    assert dag is not None
    assert dag.has_task(START_PROCESSING_NOTICE_TASK_ID)
    start_processing_notice_task = dag.get_task(START_PROCESSING_NOTICE_TASK_ID)
    assert start_processing_notice_task
    print(type(start_processing_notice_task))
    # start_processing_notice_task.execute()
    run_task(start_processing_notice_task,
             conf={"notice_id": "429421_2016", "notice_status": "RAW"})
    # start_processing_notice_task.run(
    #     start_date=dag.default_args["start_date"],
    #     end_date=dag.default_args["start_date"],
    #     conf={"notice_id": "429421_20160", "notice_status": "RAW"})

    # dag.run(start_date=datetime.now(),
    #         end_date=datetime.now()+timedelta(minutes=1),
    #         run_at_least_once=True,
    #         local=True,
    #         conf={"notice_id": "429421_20160", "notice_status": "RAW"}
    #         )
    # dag_run = dag.create_dagrun(
    #     run_id ='trig__' + datetime.now().isoformat(),
    #     state= State.RUNNING,
    #     conf={"notice_id": "429421_20160", "notice_status": "RAW"},
    #     external_trigger = True,
    #     run_type=DagRunType.MANUAL)

    # start_processing_notice_task = dag_run.get_task_instance(task_id=START_PROCESSING_NOTICE_TASK_ID)
    # start_processing_notice_task.run()
    # # ti = dag_run.get_task_instance(task_id=START_PROCESSING_NOTICE_TASK_ID)
    # # ti.refresh_from_task(task=start_processing_notice_task)
    # # ti.run()
    # result = start_processing_notice_task.run(
    #     start_date=dag.default_args["start_date"],
    #     end_date=dag.default_args["start_date"],
    # )
    # print(result)
