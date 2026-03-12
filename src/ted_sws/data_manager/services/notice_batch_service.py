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

    This function takes a list of notice IDs and queries MongoDB to determine the current
    status of each notice. Notices are then grouped by their status, and each group is
    assigned the appropriate pipeline step based on NOTICE_STATUS_TO_PIPELINE_STEP mapping.

    For example:
        - Notices with status RAW will start from normalisation pipeline
        - Notices with status DISTILLED will start from validation pipeline
        - Notices with status PACKAGED will start from publish pipeline

    Args:
        notice_ids: List of notice TED IDs to group (e.g., ["123456-2022", "234567-2022"])
        mongodb_client: Optional MongoDB client. If not provided, connects
            to the configured MongoDB instance using config.MONGO_DB_AUTH_URL.

    Returns:
        List of NoticeStatusBatch objects, each containing:
            - notice_status: The NoticeStatus enum for this group
            - notice_ids: List of TED IDs belonging to this status
            - start_with_step_name: The pipeline task ID to start processing from
    """
    # Step 1: Use defaultdict to group notices by their status
    notices_by_status = defaultdict(list)

    # Step 2: Initialize MongoDB client and repository (or use injected one for testing)
    if mongodb_client is None:
        mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)

    # Step 3: Query MongoDB for notices matching the provided IDs, retrieve only ted_id and status fields
    for notice_dict in notice_repository.collection.find(
            {NOTICE_TED_ID: {"$in": notice_ids}},
            {NOTICE_TED_ID: 1, NOTICE_STATUS: 1}
    ):
        ted_id = notice_dict[NOTICE_TED_ID]
        status_str = notice_dict.get(NOTICE_STATUS)

        # Step 4: For each notice found, extract status and add to appropriate group if status has a pipeline mapping
        if status_str:
            status = NoticeStatus[status_str]
            if status in NOTICE_STATUS_TO_PIPELINE_STEP:
                notices_by_status[status].append(ted_id)

    # Step 5: Convert grouped notices into NoticeStatusBatch objects with appropriate pipeline steps
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

    This function queries MongoDB for notices matching a specific reprocess status category.
    The reprocess status is a user-friendly display name (e.g., "Unvalidated", "Unpublished")
    that maps to multiple underlying NoticeStatus enums via REPROCESS_STATUS_DISPLAY_MAP.

    The function then queries for notices with any of the underlying statuses and returns
    them as a single batch with the appropriate pipeline step.

    Supported reprocess_status values:
        - "Unnormalised": Notices with RAW status -> start from normalisation
        - "Unvalidated": Notices with DISTILLED status -> start from validation
        - "Untransformed": Notices with NORMALISED_METADATA, INELIGIBLE_FOR_TRANSFORMATION,
          ELIGIBLE_FOR_TRANSFORMATION, PREPROCESSED_FOR_TRANSFORMATION, TRANSFORMED, DISTILLED
          -> start from transformation
        - "Unpackaged": Notices with VALIDATED, INELIGIBLE_FOR_PACKAGING, ELIGIBLE_FOR_PACKAGING
          -> start from packaging
        - "Unpublished": Notices with ELIGIBLE_FOR_PUBLISHING, INELIGIBLE_FOR_PUBLISHING,
          PACKAGED, PUBLICLY_UNAVAILABLE -> start from publishing
        - "Published": Notices with PUBLICLY_AVAILABLE, PUBLISHED -> start from transformation

    Args:
        reprocess_status: Display status name (e.g., "Unvalidated", "Unpublished", "Unnormalised")
        start_date: Optional filter for start of publication date range (format: YYYY-MM-DD)
        end_date: Optional filter for end of publication date range (format: YYYY-MM-DD)

    Returns:
        List containing a single NoticeStatusBatch if notices are found, empty list otherwise.
        The batch contains:
            - notice_status: The primary NoticeStatus enum for this category
            - notice_ids: All TED IDs matching any of the underlying statuses
            - start_with_step_name: The pipeline task ID to start processing from
    """
    # Step 1: Validate reprocess_status is a known display category
    if reprocess_status not in REPROCESS_STATUS_DISPLAY_MAP:
        return []

    # Step 2: Get the list of NoticeStatus enums and corresponding pipeline step for this category
    notice_statuses = REPROCESS_STATUS_DISPLAY_MAP[reprocess_status]
    pipeline_step = REPROCESS_STATUS_TO_PIPELINE_STEP[reprocess_status]

    # Step 3: Query MongoDB for each notice status and collect all matching notice IDs
    all_notice_ids = []
    for status in notice_statuses:
        notice_ids = notice_ids_selector_by_status(
            notice_statuses=[status],
            start_date=start_date,
            end_date=end_date
        )
        all_notice_ids.extend(notice_ids)

    # Step 4: Return empty list if no notices found for this category
    if not all_notice_ids:
        return []

    # Step 5: Create a single batch with all notice IDs and the appropriate pipeline step
    batch = NoticeStatusBatch(
        notice_status=notice_statuses[0],
        notice_ids=all_notice_ids,
        start_with_step_name=pipeline_step
    )

    return [batch]
