"""
DAG to update daily notices metadata from TED.
"""

from datetime import date, datetime, timedelta

from airflow.decorators import dag, task
from airflow.models import Param
from airflow.timetables.trigger import CronTriggerTimetable

from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import get_dag_param
from ted_sws.supra_notice_manager.services.daily_notices_metadata_services import \
    update_daily_notices_metadata_from_ted, \
    update_daily_notices_metadata_with_fetched_data

START_DATE_PARAM_KEY = "start_date"
END_DATE_PARAM_KEY = "end_date"
DEFAULT_TED_API_START_DATE = "2014-01-01"
DEFAULT_TED_API_START_DATE_FORMAT = "%Y-%m-%d"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     tags=['daily', "dashboards", "metadata", "ted", "notices"],
     catchup=False,
     timetable=CronTriggerTimetable('0 19 * * *', timezone='UTC'),
     description=__doc__[0: __doc__.find(".")],
     doc_md=__doc__,
     params={
         START_DATE_PARAM_KEY: Param(
             default=f"{date.today()}",
             type="string",
             format="date",
             title="Start Date",
             description="""This field is required.
                    Start date of the date range to fetch notices from TED."""
         ),
         END_DATE_PARAM_KEY: Param(
             default=f"{date.today()}",
             type="string",
             format="date",
             title="End Date",
             description="""This field is required.
                    End date of the date range to fetch notices from TED."""
         )
     }
     )
def daily_notices_metadata_update():
    @task
    def update_daily_notices_metadata_from_ted_api():
        start_date = get_dag_param(key=START_DATE_PARAM_KEY, raise_error=False)
        end_date = get_dag_param(key=END_DATE_PARAM_KEY, raise_error=False)

        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            start_date = datetime.strptime(DEFAULT_TED_API_START_DATE, DEFAULT_TED_API_START_DATE_FORMAT)
            end_date = datetime.today() - timedelta(days=1)

        update_daily_notices_metadata_from_ted(start_date=start_date, end_date=end_date)

    @task
    def update_daily_notices_metadata_with_fetched_data_from_repo():
        start_date = get_dag_param(key=START_DATE_PARAM_KEY, raise_error=False)
        end_date = get_dag_param(key=END_DATE_PARAM_KEY, raise_error=False)

        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            start_date = datetime.strptime(DEFAULT_TED_API_START_DATE, DEFAULT_TED_API_START_DATE_FORMAT)
            end_date = datetime.today() - timedelta(days=1)

        update_daily_notices_metadata_with_fetched_data(start_date=start_date, end_date=end_date)

    update_daily_notices_metadata_from_ted_api() >> update_daily_notices_metadata_with_fetched_data_from_repo()


dag = daily_notices_metadata_update()
