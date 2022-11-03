from typing import Any, Protocol, List
from uuid import uuid4
from airflow.models import BaseOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from pymongo import MongoClient

from dags.dags_utils import pull_dag_upstream, push_dag_downstream, chunks, get_dag_param, smart_xcom_pull, \
    smart_xcom_push
from dags.pipelines.pipeline_protocols import NoticePipelineCallable
from ted_sws import config
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.event_manager.model.event_message import EventMessage, NoticeEventMessage
from ted_sws.event_manager.services.log import log_error
from ted_sws.event_manager.services.logger_from_context import get_logger

NOTICE_IDS_KEY = "notice_ids"
START_WITH_STEP_NAME_KEY = "start_with_step_name"
EXECUTE_ONLY_ONE_STEP_KEY = "execute_only_one_step"
DEFAULT_NUBER_OF_CELERY_WORKERS = 144
NOTICE_PROCESS_WORKFLOW_DAG_NAME = "notice_process_workflow"
DEFAULT_START_WITH_TASK_ID = "notice_normalisation_pipeline"
DEFAULT_PIPELINE_NAME_FOR_LOGS = "unknown_pipeline_name"


class BatchPipelineCallable(Protocol):

    def __call__(self, notice_ids: List[str], mongodb_client: MongoClient) -> List[str]:
        """
        :param notice_ids:
        :param mongodb_client:
        :return: List of notice_ids what was processed.
        """


class NoticeBatchPipelineOperator(BaseOperator):
    """

    """

    ui_color = '#e7cff6'
    ui_fgcolor = '#000000'

    def __init__(self, *args,
                 notice_pipeline_callable: NoticePipelineCallable = None,
                 batch_pipeline_callable: BatchPipelineCallable = None,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.notice_pipeline_callable = notice_pipeline_callable
        self.batch_pipeline_callable = batch_pipeline_callable

    def execute(self, context: Any):
        """
            This method can execute the notice_pipeline_callable for each notice_id in the notice_ids batch or
            can execute the batch_pipeline_callable for whole notice_ids batch at once.
        """
        logger = get_logger()
        notice_ids = smart_xcom_pull(key=NOTICE_IDS_KEY)
        if not notice_ids:
            raise Exception(f"XCOM key [{NOTICE_IDS_KEY}] is not present in context!")
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        processed_notice_ids = []
        pipeline_name = DEFAULT_PIPELINE_NAME_FOR_LOGS
        if self.notice_pipeline_callable:
            pipeline_name = self.notice_pipeline_callable.__name__
        elif self.batch_pipeline_callable:
            pipeline_name = self.batch_pipeline_callable.__name__
        number_of_notices = len(notice_ids)
        batch_event_message = EventMessage(
            message=f"Batch processing for pipeline = [{pipeline_name}] with {number_of_notices} notices.",
            kwargs={"pipeline_name": pipeline_name,
                    "number_of_notices": number_of_notices}
        )
        batch_event_message.start_record()
        if self.batch_pipeline_callable is not None:
            processed_notice_ids.extend(
                self.batch_pipeline_callable(notice_ids=notice_ids, mongodb_client=mongodb_client))
        elif self.notice_pipeline_callable is not None:
            for notice_id in notice_ids:
                try:
                    notice_event = NoticeEventMessage(notice_id=notice_id, domain_action=pipeline_name)
                    notice_event.start_record()
                    notice = notice_repository.get(reference=notice_id)
                    result_notice_pipeline = self.notice_pipeline_callable(notice, mongodb_client)
                    if result_notice_pipeline.store_result:
                        notice_repository.update(notice=result_notice_pipeline.notice)
                    if result_notice_pipeline.processed:
                        processed_notice_ids.append(notice_id)
                    notice_event.end_record()
                    logger.info(event_message=notice_event)
                except Exception as e:
                    log_error(message=str(e))
        batch_event_message.end_record()
        logger.info(event_message=batch_event_message)
        if not processed_notice_ids:
            raise Exception(f"No notice has been processed!")
        smart_xcom_push(key=NOTICE_IDS_KEY, value=processed_notice_ids)


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
