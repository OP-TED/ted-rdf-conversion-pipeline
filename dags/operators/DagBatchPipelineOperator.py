from typing import Any

from airflow.models import BaseOperator
from pymongo import MongoClient

from dags.dags_utils import pull_dag_upstream, push_dag_downstream
from dags.pipelines.pipeline_protocols import NoticePipelineCallable
from ted_sws import config
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.event_manager.services.log import log_error

NOTICE_IDS_KEY = "notice_ids"


class NoticeBatchPipelineOperator(BaseOperator):
    """

    """

    ui_color = '#e7cff6'
    ui_fgcolor = '#000000'

    def __init__(
            self,
            python_callable: NoticePipelineCallable,
            *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.python_callable = python_callable

    def execute(self, context: Any):
        """
            This method executes the python_callable for each notice_id in the notice_ids batch.
        """
        notice_ids = pull_dag_upstream(key=NOTICE_IDS_KEY)
        if notice_ids:
            raise Exception(f"XCOM key=[{NOTICE_IDS_KEY}] is not present in context!")
        notice_repository = NoticeRepository(mongodb_client=MongoClient(config.MONGO_DB_AUTH_URL))
        processed_notice_ids = []
        for notice_id in notice_ids:
            try:
                notice = notice_repository.get(reference=notice_id)
                result_notice_pipeline = self.python_callable(notice)
                if result_notice_pipeline.store_result:
                    notice_repository.update(notice=result_notice_pipeline.notice)
                if result_notice_pipeline.processed:
                    processed_notice_ids.append(notice_id)
            except Exception as e:
                log_error(message=str(e))
        push_dag_downstream(key=NOTICE_IDS_KEY, value=processed_notice_ids)
