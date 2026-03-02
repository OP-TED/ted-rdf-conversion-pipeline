from collections import defaultdict
from typing import List, Optional

from pymongo import MongoClient

from src.dags import NOTICE_STATUS_TO_PIPELINE_STEP, REPROCESS_STATUS_DISPLAY_MAP, REPROCESS_STATUS_TO_PIPELINE_STEP
from src.dags.pipelines.notice_selectors_pipelines import notice_ids_selector_by_status
from src.ted_sws import config
from src.ted_sws.core.model.notice import NoticeStatus
from src.ted_sws.data_manager.adapters.notice_repository import NoticeRepository, NOTICE_TED_ID, NOTICE_STATUS
from src.ted_sws.data_manager.models.notice_batch import NoticeStatusBatch


def group_notice_ids_by_status(notice_ids: List[str], mongodb_client=None) -> List[NoticeStatusBatch]:
    """
    Group notice IDs by their current status and map to pipeline steps.
    
    Args:
        notice_ids: List of notice IDs to group
        mongodb_client: Optional MongoDB client (for testing)
        
    Returns:
        List of NoticeStatusBatch objects, each containing notices with the same status
    """
    notices_by_status = defaultdict(list)

    if mongodb_client is None:
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)

    for notice_dict in notice_repository.collection.find(
            {NOTICE_TED_ID: {"$in": notice_ids}},
            {NOTICE_TED_ID: 1, NOTICE_STATUS: 1}
    ):
        ted_id = notice_dict[NOTICE_TED_ID]
        status_str = notice_dict.get(NOTICE_STATUS)

        if status_str:
            status = NoticeStatus[status_str]
            if status in NOTICE_STATUS_TO_PIPELINE_STEP:
                notices_by_status[status].append(ted_id)

    batches = []
    for status, ids in notices_by_status.items():
        if ids:
            pipeline_step = NOTICE_STATUS_TO_PIPELINE_STEP[status]
            batch = NoticeStatusBatch(
                notice_status=status,
                notice_ids=ids,
                start_with_step_name=pipeline_step
            )
            batches.append(batch)

    return batches


def group_notice_ids_by_reprocess_status(
        reprocess_status: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
) -> List[NoticeStatusBatch]:
    """
    Group notice IDs by reprocess status display category.
    
    Args:
        reprocess_status: Single display status name (e.g., "Unvalidated", "Unpublished")
        start_date: Filter by start publication date
        end_date: Filter by end publication date
        
    Returns:
        List of NoticeStatusBatch (usually single batch)
    """
    if reprocess_status not in REPROCESS_STATUS_DISPLAY_MAP:
        return []

    notice_statuses = REPROCESS_STATUS_DISPLAY_MAP[reprocess_status]
    pipeline_step = REPROCESS_STATUS_TO_PIPELINE_STEP[reprocess_status]

    all_notice_ids = []
    for status in notice_statuses:
        notice_ids = notice_ids_selector_by_status(
            notice_statuses=[status],
            start_date=start_date,
            end_date=end_date
        )
        all_notice_ids.extend(notice_ids)

    if not all_notice_ids:
        return []

    batch = NoticeStatusBatch(
        notice_status=notice_statuses[0],
        notice_ids=all_notice_ids,
        start_with_step_name=pipeline_step
    )

    return [batch]
