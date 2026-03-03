from airflow.decorators import dag, task
from airflow.models import Param

from src.dags import DEFAULT_DAG_ARGUMENTS, NOTICE_NORMALISATION_PIPELINE_TASK_ID, RUN_MATERIALISED_VIEW_DAG_PARAM, \
    RUN_MATERIALISED_VIEW_DAG_PARAM_DESCRIPTION, START_FROM_NORMALISATION_DAG_PARAM
from src.dags.dags_utils import get_dag_param, push_dag_downstream
from src.dags.operators.DagBatchPipelineOperator import NOTICE_IDS_KEY, TriggerNoticeBatchPipelineOperator, \
    MAX_BATCH_SIZE
from src.ted_sws.core.model.notice import NoticeStatus
from src.ted_sws.data_manager.models.notice_batch import NoticeStatusBatch
from src.ted_sws.data_manager.services.notice_batch_service import group_notice_ids_by_status
from src.ted_sws.event_manager.adapters.event_log_decorator import event_log
from src.ted_sws.event_manager.model.event_message import TechnicalEventMessage, EventMessageMetadata, \
    EventMessageProcessType

DAG_ID = "reprocess_notices_by_id_from_backlog"
DAG_NAME = "Reprocess notices from backlog by ID"

NOTICE_IDS_DAG_PARAM = "notice_ids"
TRIGGER_NOTICE_PROCESS_WORKFLOW_TASK_ID = "trigger_notice_process_workflow"


@dag(
    default_args=DEFAULT_DAG_ARGUMENTS,
    dag_id=DAG_ID,
    dag_display_name=DAG_NAME,
    schedule_interval=None,
    tags=["selector", "re-transform"],
    params={
        NOTICE_IDS_DAG_PARAM: Param(
            type="array",
            title="Notice IDs",
            description="Required. List of TED Notice IDs to reprocess. Each value should be entered on a new line. Example: [\"123456-2022\", \"456789-2023\"]. Every ID value should be entered on a newline"
        ),
        RUN_MATERIALISED_VIEW_DAG_PARAM: Param(
            default=False,
            type="boolean",
            title="Run Materialised View",
            description=RUN_MATERIALISED_VIEW_DAG_PARAM_DESCRIPTION
        ),
        START_FROM_NORMALISATION_DAG_PARAM: Param(
            default=False,
            type="boolean",
            title="Start from Normalisation",
            description="If enabled, start reprocessing from normalisation. If disabled, automatically map each notice's current status to determine pipeline start step."
        ),
    },
    description="Reprocess specific TED notices by their IDs, with option to start from normalisation or auto-map by current status"
)
def reprocess_notices_by_id_from_backlog():
    """
    DAG for reprocessing specific notices by their IDs.

    This DAG allows users to reprocess a list of TED notice IDs. It supports two modes:
    1. Start from normalisation: All notices start from the normalisation pipeline step
    2. Auto-map by status: Each notice's current status is used to determine the appropriate
       pipeline step (e.g., RAW notices start from normalisation, DISTILLED from validation)
    """

    @task
    @event_log(TechnicalEventMessage(
        message="select_notices_for_reprocess_by_id",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG,
            process_name=DAG_ID
        ))
    )
    def select_notice_ids():
        """
        Select and group notice IDs for reprocessing.

        Logic:
            1. Retrieve the list of notice IDs from DAG parameters
            2. Check if start_from_normalisation is enabled:
               - If True: Create a single batch with all notices starting from normalisation
               - If False: Query each notice's current status and group them accordingly
            3. Return list of NoticeStatusBatch objects for downstream processing
        """
        notice_ids = get_dag_param(key=NOTICE_IDS_DAG_PARAM, raise_error=True)

        if not notice_ids:
            raise Exception("No notice IDs provided.")

        start_from_normalisation = get_dag_param(key=START_FROM_NORMALISATION_DAG_PARAM)

        # Mode 1: Start all notices from normalisation
        if start_from_normalisation:
            batch = NoticeStatusBatch(
                notice_ids=notice_ids,
                start_with_step_name=NOTICE_NORMALISATION_PIPELINE_TASK_ID,
                notice_status=NoticeStatus.RAW
            )

            return [batch.model_dump()]

        # Mode 2: Auto-map each notice's status to appropriate pipeline step
        notice_batches = group_notice_ids_by_status(notice_ids)

        return [dto.model_dump() for dto in notice_batches]

    @task
    def push_notice_ids_for_batch(batch: dict):
        """
        Push notice IDs to XCom for downstream batch processing.

        Each batch contains a list of notice IDs that will be processed together
        in the TriggerNoticeBatchPipelineOperator.
        """
        push_dag_downstream(key=NOTICE_IDS_KEY, value=batch["notice_ids"])

    # Dynamic task mapping: The number of batches determines the number of parallel tasks
    # Each batch contains notices with the same status, so they can be processed together
    batches = select_notice_ids()

    # Expand push_notice_ids_for_batch into multiple parallel tasks, one per batch
    # This pushes each batch's notice IDs to XCom for the trigger task to consume
    push_context = push_notice_ids_for_batch.expand(batch=batches)

    # Create trigger tasks that dynamically map the start_with_step_name for each batch
    # Each batch may have a different pipeline step based on notice status:
    #   - RAW -> normalisation
    #   - DISTILLED -> validation
    #   - PACKAGED -> publishing, etc.
    # The .expand() with batches.map() creates one trigger task per batch with its
    # corresponding start step
    trigger = TriggerNoticeBatchPipelineOperator.partial(
        task_id=TRIGGER_NOTICE_PROCESS_WORKFLOW_TASK_ID,
        batch_size=MAX_BATCH_SIZE,
    ).expand(
        start_with_step_name=batches.map(lambda batch: batch["start_with_step_name"])
    )

    # Ensure push tasks complete before trigger tasks start
    trigger.set_upstream(push_context)


dag = reprocess_notices_by_id_from_backlog()
