from airflow.decorators import dag, task
from airflow.models import Param

from src.dags import DEFAULT_DAG_ARGUMENTS, NOTICE_NORMALISATION_PIPELINE_TASK_ID, RUN_MATERIALISED_VIEW_DAG_PARAM, \
    RUN_MATERIALISED_VIEW_DAG_PARAM_DESCRIPTION, START_FROM_NORMALISATION_DAG_PARAM, \
    REPROCESS_STATUS_LIST, REPROCESS_STATUS_DISPLAY_MAP
from src.dags.dags_utils import push_dag_downstream, get_dag_param
from src.dags.operators.DagBatchPipelineOperator import NOTICE_IDS_KEY, TriggerNoticeBatchPipelineOperator, \
    MAX_BATCH_SIZE
from src.dags.pipelines.notice_selectors_pipelines import notice_ids_selector_by_status
from src.ted_sws.core.model.notice import NoticeStatus
from src.ted_sws.data_manager.models.notice_batch import NoticeStatusBatch
from src.ted_sws.data_manager.services.notice_batch_service import group_notice_ids_by_reprocess_status
from src.ted_sws.event_manager.adapters.event_log_decorator import event_log
from src.ted_sws.event_manager.model.event_message import TechnicalEventMessage, EventMessageMetadata, \
    EventMessageProcessType

DAG_ID = "reprocess_notices_from_backlog_by_status"
DAG_NAME = "Reprocess notices from backlog by status"

TRIGGER_NOTICE_PROCESS_WORKFLOW_TASK_ID = "trigger_notice_process_workflow"
START_DATE_DAG_PARAM = "start_date"
END_DATE_DAG_PARAM = "end_date"
NOTICE_STATUSES_DAG_PARAM = "notice_statuses"


@dag(
    default_args=DEFAULT_DAG_ARGUMENTS,
    dag_id=DAG_ID,
    dag_display_name=DAG_NAME,
    schedule_interval=None,
    tags=['selector', 're-transform'],
    params={
        NOTICE_STATUSES_DAG_PARAM: Param(
            default=[],
            type=["string"],
            title="Notice Statuses",
            description="Required. Select one or more notice statuses to reprocess.",
            enum=REPROCESS_STATUS_LIST
        ),
        START_DATE_DAG_PARAM: Param(default="", type=["null", "string"], format="date",
                                    description="Start publication date (YYYY-MM-DD)"),
        END_DATE_DAG_PARAM: Param(default="", type=["null", "string"], format="date",
                                  description="End publication date (YYYY-MM-DD)"),
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
            description="If enabled, start reprocessing from normalisation. If disabled, automatically map notice statuses to determine pipeline start step."
        )
    },
    description="Reprocess TED notices by status category (e.g., Unvalidated, Unpublished), with optional date filtering"
)
def reprocess_notices_from_backlog_by_status():
    """
    DAG for reprocessing notices by their status category.

    This DAG allows users to select and reprocess notices based on user-friendly status categories
    (like "Unvalidated", "Unpublished", "Unnormalised") which map to multiple underlying notice
    statuses in the system. It supports optional date filtering and two processing modes:

    1. Start from normalisation: All matching notices start from the normalisation pipeline step
    2. Auto-map by status: Each notice's current status determines the appropriate pipeline step

    Supported status categories:
        - Unnormalised: Notices with RAW status
        - Unvalidated: Notices with DISTILLED status
        - Untransformed: Notices at various transformation stages
        - Unpackaged: Notices at packaging stages
        - Unpublished: Notices at publishing stages
        - Published: Currently published notices
    """

    @task
    @event_log(TechnicalEventMessage(
        message="select_notices_for_re_transform",
        metadata=EventMessageMetadata(
            process_type=EventMessageProcessType.DAG,
            process_name=DAG_ID
        ))
    )
    def select_notice_ids():
        """
        Select and group notice IDs by reprocess status category.

        Logic:
            1. Retrieve parameters: status category, date range, and processing mode
            2. Check if start_from_normalisation is enabled:
               - If True: Query all notices in the selected category and create a single
                 batch starting from normalisation
               - If False: Use group_notice_ids_by_reprocess_status to map each notice's
                 status to the appropriate pipeline step
            3. Return list of NoticeStatusBatch objects for downstream processing
        """
        start_date = get_dag_param(key=START_DATE_DAG_PARAM, default_value="")
        end_date = get_dag_param(key=END_DATE_DAG_PARAM, default_value="")
        statuses_param = get_dag_param(key=NOTICE_STATUSES_DAG_PARAM)
        start_from_normalisation = get_dag_param(key=START_FROM_NORMALISATION_DAG_PARAM, default_value=False)

        # Mode 1: Start all matching notices from normalisation
        if start_from_normalisation:
            # Get the underlying NoticeStatus enums for the selected category
            notice_statuses = REPROCESS_STATUS_DISPLAY_MAP.get(statuses_param, [])

            # Query notices for each underlying status with optional date filtering
            all_notice_ids = []
            for status in notice_statuses:
                ids = notice_ids_selector_by_status(
                    notice_statuses=[status],
                    start_date=start_date if start_date else None,
                    end_date=end_date if end_date else None
                )
                all_notice_ids.extend(ids)

            batch = NoticeStatusBatch(
                notice_ids=all_notice_ids,
                start_with_step_name=NOTICE_NORMALISATION_PIPELINE_TASK_ID,
                notice_status=NoticeStatus.RAW
            )

            return [batch.model_dump()]

        # Mode 2: Auto-map each notice's status to appropriate pipeline step
        notice_batches = group_notice_ids_by_reprocess_status(
            reprocess_status=statuses_param,
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None
        )

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
    # Each batch may have a different pipeline step based on the reprocess status category:
    #   - Unnormalised -> normalisation
    #   - Unvalidated -> validation
    #   - Untransformed -> transformation
    #   - Unpackaged -> packaging
    #   - Unpublished -> publishing
    # The .expand() with batches.map() creates one trigger task per batch with its
    # corresponding start step
    trigger = TriggerNoticeBatchPipelineOperator.partial(
        task_id=TRIGGER_NOTICE_PROCESS_WORKFLOW_TASK_ID,
        batch_size=MAX_BATCH_SIZE,
    ).expand(
        start_with_step_name=batches.map(lambda batch: batch["start_with_step_name"]))

    # Ensure push tasks complete before trigger tasks start
    trigger.set_upstream(push_context)


dag = reprocess_notices_from_backlog_by_status()
