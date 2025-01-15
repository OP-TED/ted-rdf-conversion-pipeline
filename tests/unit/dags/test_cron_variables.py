import pytest
from airflow.timetables.trigger import CronTriggerTimetable

from ted_sws import config


def test_valid_cron_expression(example_cron_table: str, example_dag_cron_table: CronTriggerTimetable):
    """Test that a valid cron expression is correctly parsed into a CronTriggerTimetable"""
    assert isinstance(example_dag_cron_table, CronTriggerTimetable)
    assert example_dag_cron_table._expression == example_cron_table
    assert example_dag_cron_table._timezone.name == "UTC"
    assert example_dag_cron_table.description != ""


def test_invalid_cron_expression(example_wrong_cron_table: str):
    """Test that an invalid cron expression raises an error"""
    with pytest.raises(Exception):
        CronTriggerTimetable(cron=example_wrong_cron_table, timezone="UTC")


def test_schedule_variable_names(dag_fetch_schedule_variable_name: str,
                                 dag_materialised_view_update_schedule_variable_name: str):
    """Test that schedule variable names are properly set"""

    assert f'{config.SCHEDULE_DAG_FETCH=}'.split('=')[0] == f"config.{dag_fetch_schedule_variable_name}"
    assert f'{config.SCHEDULE_DAG_MATERIALIZED_VIEW_UPDATE=}'.split('=')[
               0] == f"config.{dag_materialised_view_update_schedule_variable_name}"
