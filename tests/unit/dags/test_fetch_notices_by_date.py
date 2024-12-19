from airflow import DAG
from airflow.models import DagBag, Variable
from airflow.timetables.trigger import CronTriggerTimetable

from dags.fetch_notices_by_date import DAG_FETCH_DEFAULT_TIMETABLE, DAG_FETCH_DEFAULT_TIMEZONE, \
    SCHEDULE_DAG_FETCH_VAR_NAME


def test_schedule_dag_fetch_ver_name_is_correct(dag_fetch_schedule_variable_name):
    assert SCHEDULE_DAG_FETCH_VAR_NAME == dag_fetch_schedule_variable_name


def test_fetcher_has_default_timetable_at_the_beginning(dag_bag: DagBag, fetcher_dag_id: str):
    fetcher_dag: DAG = dag_bag.get_dag(dag_id=fetcher_dag_id)
    default_dag_timetable = CronTriggerTimetable(cron=DAG_FETCH_DEFAULT_TIMETABLE,
                                                 timezone=DAG_FETCH_DEFAULT_TIMEZONE)

    assert fetcher_dag is not None
    assert fetcher_dag.schedule_interval == default_dag_timetable._expression


def test_fetcher_gets_correct_timetable_after_reparse(dag_bag: DagBag, fetcher_dag_id: str,
                                                      example_dag_cron_table: CronTriggerTimetable,
                                                      airflow_timetable_import_error_name: str):
    fetcher_dag: DAG = dag_bag.get_dag(dag_id=fetcher_dag_id)
    assert fetcher_dag is not None
    assert fetcher_dag.schedule_interval != example_dag_cron_table._expression

    Variable.set(key=SCHEDULE_DAG_FETCH_VAR_NAME, value=example_dag_cron_table._expression)
    dag_bag.collect_dags(only_if_updated=False)

    fetcher_dag: DAG = dag_bag.get_dag(dag_id=fetcher_dag_id)
    assert fetcher_dag is not None
    assert fetcher_dag.schedule_interval == example_dag_cron_table._expression

    assert all(airflow_timetable_import_error_name not in error for error in dag_bag.import_errors.values())


def test_fetcher_gets_incorrect_timetable_after_reparse(dag_bag: DagBag, fetcher_dag_id: str,
                                                        example_wrong_cron_table: str,
                                                        airflow_timetable_import_error_name: str):
    fetcher_dag: DAG = dag_bag.get_dag(dag_id=fetcher_dag_id)
    assert fetcher_dag is not None
    default_dag_timetable = CronTriggerTimetable(cron=DAG_FETCH_DEFAULT_TIMETABLE,
                                                 timezone=DAG_FETCH_DEFAULT_TIMEZONE)
    assert fetcher_dag.schedule_interval == default_dag_timetable._expression

    Variable.set(key=SCHEDULE_DAG_FETCH_VAR_NAME, value=example_wrong_cron_table)
    dag_bag.collect_dags(only_if_updated=False)

    assert any(airflow_timetable_import_error_name in error for error in dag_bag.import_errors.values())
