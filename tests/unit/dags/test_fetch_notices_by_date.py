import os

from airflow import DAG
from airflow.models import DagBag, Variable
from airflow.timetables.trigger import CronTriggerTimetable

from dags.fetch_notices_by_date import DAG_FETCH_DEFAULT_TIMEZONE
from ted_sws import DAG_FETCH_DEFAULT_TIMETABLE


def test_fetcher_change_timetable_from_airflow_variable_after_reparse(dag_bag: DagBag,
                                                                      dag_fetch_schedule_variable_name,
                                                                      fetcher_dag_id: str,
                                                                      example_dag_cron_table: CronTriggerTimetable,
                                                                      airflow_timetable_import_error_name: str):
    fetcher_dag: DAG = dag_bag.get_dag(dag_id=fetcher_dag_id)
    assert fetcher_dag is not None
    assert fetcher_dag.schedule_interval != example_dag_cron_table._expression

    Variable.set(key=dag_fetch_schedule_variable_name, value=example_dag_cron_table._expression)
    dag_bag.collect_dags(only_if_updated=False)

    fetcher_dag: DAG = dag_bag.get_dag(dag_id=fetcher_dag_id)
    assert fetcher_dag is not None
    assert fetcher_dag.schedule_interval == example_dag_cron_table._expression

    assert all(airflow_timetable_import_error_name not in error for error in dag_bag.import_errors.values())


def test_fetcher_change_timetable_from_env_variable_after_reparse(dag_bag: DagBag,
                                                                  dag_fetch_schedule_variable_name: str,
                                                                  fetcher_dag_id: str,
                                                                  example_dag_cron_table: CronTriggerTimetable,
                                                                  airflow_timetable_import_error_name: str):
    fetcher_dag: DAG = dag_bag.get_dag(dag_id=fetcher_dag_id)
    assert fetcher_dag is not None
    assert fetcher_dag.schedule_interval != example_dag_cron_table._expression

    os.environ[dag_fetch_schedule_variable_name] = example_dag_cron_table._expression
    dag_bag.collect_dags(only_if_updated=False)

    fetcher_dag: DAG = dag_bag.get_dag(dag_id=fetcher_dag_id)
    assert fetcher_dag is not None
    assert fetcher_dag.schedule_interval == example_dag_cron_table._expression

    assert all(airflow_timetable_import_error_name not in error for error in dag_bag.import_errors.values())


def test_fetcher_gets_incorrect_timetable_after_reparse(dag_bag: DagBag,
                                                        dag_fetch_schedule_variable_name: str,
                                                        fetcher_dag_id: str,
                                                        example_wrong_cron_table: str,
                                                        airflow_timetable_import_error_name: str):
    fetcher_dag: DAG = dag_bag.get_dag(dag_id=fetcher_dag_id)
    assert fetcher_dag is not None
    default_dag_timetable = CronTriggerTimetable(cron=DAG_FETCH_DEFAULT_TIMETABLE,
                                                 timezone=DAG_FETCH_DEFAULT_TIMEZONE)
    assert fetcher_dag.schedule_interval == default_dag_timetable._expression

    Variable.set(key=dag_fetch_schedule_variable_name, value=example_wrong_cron_table)
    dag_bag.collect_dags(only_if_updated=False)

    assert any(airflow_timetable_import_error_name in error for error in dag_bag.import_errors.values())
