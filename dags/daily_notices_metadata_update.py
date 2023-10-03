"""
DAG to update daily notices metadata from TED.
"""

from datetime import date, datetime

from airflow.models import Param
from airflow.decorators import dag, task

from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import get_dag_param
from ted_sws.data_manager.services.daily_notices_metadata_services import update_daily_notices_metadata_from_ted, \
    update_daily_notices_metadata_with_fetched_data

START_DATE_PARAM_KEY = "start_date"
END_DATE_PARAM_KEY = "end_date"


@dag(default_args=DEFAULT_DAG_ARGUMENTS,
     schedule_interval=None,
     tags=['daily', "dashboards", "metadata", "ted", "notices"],
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
        start_date = get_dag_param(key=START_DATE_PARAM_KEY, raise_error=True)
        end_date = get_dag_param(key=END_DATE_PARAM_KEY, raise_error=True)

        update_daily_notices_metadata_from_ted(start_date=datetime.strptime(start_date, "%Y-%m-%d"),
                                               end_date=datetime.strptime(end_date, "%Y-%m-%d"))

    @task
    def update_daily_notices_metadata_with_fetched_data_from_repo():
        start_date = get_dag_param(key=START_DATE_PARAM_KEY, raise_error=True)
        end_date = get_dag_param(key=END_DATE_PARAM_KEY, raise_error=True)

        update_daily_notices_metadata_with_fetched_data(start_date=datetime.strptime(start_date, "%Y-%m-%d"),
                                                        end_date=datetime.strptime(end_date, "%Y-%m-%d"))

    update_daily_notices_metadata_from_ted_api() >> update_daily_notices_metadata_with_fetched_data_from_repo()


dag = daily_notices_metadata_update()
