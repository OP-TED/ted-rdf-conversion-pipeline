from datetime import datetime
from typing import Any
from dateutil import rrule

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import get_dag_param
from dags.fetch_notices_by_date import WILD_CARD_DAG_KEY, TRIGGER_COMPLETE_WORKFLOW_DAG_KEY, \
    DAG_NAME as FETCH_NOTICES_BY_DATE_DAG_NAME
from ted_sws.event_manager.adapters.event_log_decorator import event_log
from ted_sws.event_manager.model.event_message import TechnicalEventMessage, EventMessageMetadata, \
    EventMessageProcessType

DAG_NAME = "fetch_notices_by_date_range"

START_DATE_KEY = "start_date"
END_DATE_KEY = "end_date"


def generate_wildcards_foreach_day_in_range(start_date: str, end_date: str) -> list:
    """
        Given a date range returns all daily dates in that range
    :param start_date:
    :param end_date:
    :return:
    """
    return [dt.strftime('%Y%m%d*')
            for dt in rrule.rrule(rrule.DAILY,
                                  dtstart=datetime.strptime(start_date, '%Y%m%d'),
                                  until=datetime.strptime(end_date, '%Y%m%d'))]


@dag(default_args=DEFAULT_DAG_ARGUMENTS, schedule_interval=None, tags=['master'])
def fetch_notices_by_date_range():
    @task
    @event_log(TechnicalEventMessage(
        message="trigger_fetch_notices_workers_for_date_range",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG, process_name=DAG_NAME
        ))
    )
    def trigger_notice_by_date_for_each_date_in_range():
        context: Any = get_current_context()
        start_date = get_dag_param(key=START_DATE_KEY, raise_error=True)
        end_date = get_dag_param(key=END_DATE_KEY, raise_error=True)
        trigger_complete_workflow = get_dag_param(key=TRIGGER_COMPLETE_WORKFLOW_DAG_KEY, default_value=False)
        date_wildcards = generate_wildcards_foreach_day_in_range(start_date, end_date)
        for date_wildcard in date_wildcards:
            TriggerDagRunOperator(
                task_id=f'trigger_notice_fetch_by_date_workflow_dag_{date_wildcard[:-1]}',
                trigger_dag_id=FETCH_NOTICES_BY_DATE_DAG_NAME,
                conf={WILD_CARD_DAG_KEY: date_wildcard,
                      TRIGGER_COMPLETE_WORKFLOW_DAG_KEY: trigger_complete_workflow,
                      }
            ).execute(context=context)

    trigger_notice_by_date_for_each_date_in_range()


dag = fetch_notices_by_date_range()
