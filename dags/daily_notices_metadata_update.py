"""
DAG to update daily notices metadata from TED.
"""

from datetime import date

from airflow.models import Param
from airflow.decorators import dag, task

from dags import DEFAULT_DAG_ARGUMENTS
from dags.dags_utils import get_dag_param

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
    def update_daily_notices_metadata_from_ted():
        start_date = get_dag_param(key=START_DATE_PARAM_KEY, raise_error=True)
        end_date = get_dag_param(key=END_DATE_PARAM_KEY, raise_error=True)

        update_daily_notices_metadata_from_ted(start_date=start_date, end_date=end_date)

    update_daily_notices_metadata_from_ted()