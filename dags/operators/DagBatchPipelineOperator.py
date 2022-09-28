from typing import Any
from uuid import uuid4
from airflow.models import BaseOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from pymongo import MongoClient

from dags.dags_utils import pull_dag_upstream, push_dag_downstream, chunks, get_dag_param
from dags.pipelines.pipeline_protocols import NoticePipelineCallable
from ted_sws import config
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.event_manager.services.log import log_error

NOTICE_IDS_KEY = "notice_ids"
START_WITH_STEP_NAME_KEY = "start_with_step_name"
EXECUTE_ONLY_ONE_STEP_KEY = "execute_only_one_step"
DEFAULT_NUBER_OF_CELERY_WORKERS = 144
NOTICE_PROCESS_WORKFLOW_DAG_NAME = "notice_process_workflow"
DEFAULT_START_WITH_TASK_ID = "notice_normalisation_pipeline"


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
        if not notice_ids:
            raise Exception(f"XCOM key [{NOTICE_IDS_KEY}] is not present in context!")
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


class TriggerNoticeBatchPipelineOperator(BaseOperator):
    ui_color = ' #1bd5ff'
    ui_fgcolor = '#000000'

    def __init__(
            self,
            *args,
            start_with_step_name: str = None,
            batch_size: int = None,
            execute_only_one_step: bool = None,
            push_result: bool = False,
            **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.start_with_step_name = start_with_step_name if start_with_step_name else DEFAULT_START_WITH_TASK_ID
        self.execute_only_one_step = execute_only_one_step
        self.push_result = push_result
        self.batch_size = batch_size

    def execute(self, context: Any):
        if self.execute_only_one_step is None:
            self.execute_only_one_step = get_dag_param(key=EXECUTE_ONLY_ONE_STEP_KEY, default_value=False)
        notice_ids = pull_dag_upstream(key=NOTICE_IDS_KEY)
        if notice_ids:
            batch_size = self.batch_size if self.batch_size else 1 + len(notice_ids) // DEFAULT_NUBER_OF_CELERY_WORKERS
            for notice_batch in chunks(notice_ids, chunk_size=batch_size):
                TriggerDagRunOperator(
                    task_id=f'trigger_worker_dag_{uuid4().hex}',
                    trigger_dag_id=NOTICE_PROCESS_WORKFLOW_DAG_NAME,
                    conf={
                        NOTICE_IDS_KEY: list(notice_batch),
                        START_WITH_STEP_NAME_KEY: self.start_with_step_name,
                        EXECUTE_ONLY_ONE_STEP_KEY: self.execute_only_one_step
                    }
                ).execute(context=context)

        if self.push_result:
            push_dag_downstream(key=NOTICE_IDS_KEY, value=notice_ids)
