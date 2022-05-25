from datetime import datetime

from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from dateutil import rrule

from dags import DEFAULT_DAG_ARGUMENTS
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context

from dags.fetch_notices_per_day_worker import DATE_WILD_CARD_KEY

START_DATE_KEY = "start_date"
END_DATE_KEY = "end_date"


def generate_daily_dates(start_date: str, end_date: str) -> list:
    """
        Given a date range returns all daily dates in that range
    :param start_date:
    :param end_date:
    :return:
    """
    return [dt.strftime('%Y%m%d')
            for dt in rrule.rrule(rrule.DAILY,
                                  dtstart=datetime.strptime(start_date, '%Y%m%d'),
                                  until=datetime.strptime(end_date, '%Y%m%d'))]


def generate_wild_card_by_date(date: str) -> str:
    """
        Method to build a wildcard_date from a date string
    :param date:
    :return:
    """
    return f"{date}*"


@dag(default_args=DEFAULT_DAG_ARGUMENTS, schedule_interval=None, tags=['master', 'fetch_notices_for_date_range'])
def fetch_notices_for_date_range():
    @task
    def trigger_fetch_notices_workers_for_date_range():
        context = get_current_context()
        dag_conf = context["dag_run"].conf

        if START_DATE_KEY not in dag_conf.keys():
            raise "Config key [start_date] is not present in dag context"
        if END_DATE_KEY not in dag_conf.keys():
            raise "Config key [end_date] is not present in dag context"

        for generated_date in generate_daily_dates(dag_conf[START_DATE_KEY], dag_conf[END_DATE_KEY]):
            wildcard_date = generate_wild_card_by_date(date=generated_date)
            TriggerDagRunOperator(
                task_id=f'trigger_fetch_notices_per_day_worker_dag_{wildcard_date}',
                trigger_dag_id="fetch_notices_per_day_worker",
                conf={DATE_WILD_CARD_KEY: wildcard_date}
            ).execute(context=context)

    trigger_fetch_notices_workers_for_date_range()


dag = fetch_notices_for_date_range()
