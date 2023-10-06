from datetime import date
from typing import Optional, List

from dateutil import rrule
from pymongo import MongoClient

from ted_sws import config
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.core.model.supra_notice import DailyNoticesMetadata
from ted_sws.data_manager.adapters.daily_notices_metadata_repository import DailyNoticesMetadataRepository
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, TedRequestAPI

TED_API_NOTICE_ID_FIELD = "ND"
TED_API_WILDCARD_DATE_FORMAT = "%Y%m%d*"
DAILY_NOTICES_METADATA_TED_API_QUERY_RESULT_FIELDS = {"fields": ["ND"]}
TED_API_QUERY_FIELD = "q"
DAILY_NOTICES_METADATA_TED_API_QUERY = {
    TED_API_QUERY_FIELD: "PD=[{aggregation_date}]"
}

NOTICE_SUCCESS_TRANSITION_DOWNSTREAM = [NoticeStatus.PUBLISHED, NoticeStatus.ELIGIBLE_FOR_PUBLISHING,
                                        NoticeStatus.PACKAGED, NoticeStatus.ELIGIBLE_FOR_PACKAGING,
                                        NoticeStatus.VALIDATED, NoticeStatus.DISTILLED,
                                        NoticeStatus.TRANSFORMED, NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION,
                                        NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION, NoticeStatus.NORMALISED_METADATA,
                                        NoticeStatus.INDEXED, NoticeStatus.RAW]

NOTICE_STATUS_COVERAGE_DOWNSTREAM_TRANSITION = {
    NoticeStatus.PUBLICLY_AVAILABLE: NOTICE_SUCCESS_TRANSITION_DOWNSTREAM,
    NoticeStatus.PUBLICLY_UNAVAILABLE: NOTICE_SUCCESS_TRANSITION_DOWNSTREAM,
    NoticeStatus.PUBLISHED: NOTICE_SUCCESS_TRANSITION_DOWNSTREAM[1:],
    NoticeStatus.ELIGIBLE_FOR_PUBLISHING: NOTICE_SUCCESS_TRANSITION_DOWNSTREAM[2:],
    NoticeStatus.INELIGIBLE_FOR_PUBLISHING: NOTICE_SUCCESS_TRANSITION_DOWNSTREAM[2:],
    NoticeStatus.PACKAGED: NOTICE_SUCCESS_TRANSITION_DOWNSTREAM[3:],
    NoticeStatus.ELIGIBLE_FOR_PACKAGING: NOTICE_SUCCESS_TRANSITION_DOWNSTREAM[4:],
    NoticeStatus.INELIGIBLE_FOR_PACKAGING: NOTICE_SUCCESS_TRANSITION_DOWNSTREAM[4:],
    NoticeStatus.VALIDATED: NOTICE_SUCCESS_TRANSITION_DOWNSTREAM[5:],
    NoticeStatus.DISTILLED: NOTICE_SUCCESS_TRANSITION_DOWNSTREAM[6:],
    NoticeStatus.TRANSFORMED: NOTICE_SUCCESS_TRANSITION_DOWNSTREAM[7:],
    NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION: NOTICE_SUCCESS_TRANSITION_DOWNSTREAM[8:],
    NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION: NOTICE_SUCCESS_TRANSITION_DOWNSTREAM[9:],
    NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION: NOTICE_SUCCESS_TRANSITION_DOWNSTREAM[9:],
    NoticeStatus.NORMALISED_METADATA: NOTICE_SUCCESS_TRANSITION_DOWNSTREAM[10:],
    NoticeStatus.INDEXED: NOTICE_SUCCESS_TRANSITION_DOWNSTREAM[11:],
}


def generate_list_of_dates_from_date_range(start_date: date, end_date: date) -> Optional[List[date]]:
    """
        Given a date range returns all daily dates in that range
    :param start_date:
    :param end_date:
    :return:
    """
    if start_date > end_date:
        return None
    return [dt.date() for dt in rrule.rrule(rrule.DAILY,
                                            dtstart=start_date,
                                            until=end_date)]


def update_daily_notices_metadata_from_ted(start_date: date,
                                           end_date: date,
                                           ted_api: TedAPIAdapter = None,
                                           daily_notices_metadata_repo: DailyNoticesMetadataRepository = None):
    """
    Updates the daily notices metadata from the TED API.
    """

    if start_date > end_date:
        raise Exception("Start date cannot be greater than end date")

    ted_api = ted_api or TedAPIAdapter(TedRequestAPI(), config.TED_API_URL)
    if not daily_notices_metadata_repo:
        mongo_client = MongoClient(config.MONGO_DB_AUTH_URL)
        daily_notices_metadata_repo = DailyNoticesMetadataRepository(mongo_client)

    # Generate list of dates from date range
    date_range = generate_list_of_dates_from_date_range(start_date, end_date)

    # Getting from metadata repository dates that are not in the repository from date range
    dates_not_in_repository = [day for day in date_range if
                               day not in daily_notices_metadata_repo.list_daily_notices_metadata_aggregation_date()]

    # Getting from TED API dates that are not in the repository from date range
    for day in dates_not_in_repository:
        ted_api_query = DAILY_NOTICES_METADATA_TED_API_QUERY.copy()
        ted_api_query[TED_API_QUERY_FIELD] = ted_api_query[TED_API_QUERY_FIELD].format(
            aggregation_date=day.strftime(TED_API_WILDCARD_DATE_FORMAT))
        notice_ids = ted_api.get_by_query(ted_api_query,
                                          result_fields=DAILY_NOTICES_METADATA_TED_API_QUERY_RESULT_FIELDS)
        daily_notices_metadata = DailyNoticesMetadata(aggregation_date=day)
        daily_notices_metadata.ted_api_notice_ids = [notice[TED_API_NOTICE_ID_FIELD] for notice in notice_ids]
        daily_notices_metadata_repo.add(daily_notices_metadata)


def update_daily_notices_metadata_with_fetched_data(start_date: date,
                                                    end_date: date,
                                                    notice_repo: NoticeRepository = None,
                                                    daily_notices_metadata_repo: DailyNoticesMetadataRepository = None):
    """
    Updates the daily notices metadata witch fetched data.
    """

    if start_date > end_date:
        raise Exception("Start date cannot be greater than end date")

    if not daily_notices_metadata_repo:
        mongo_client = MongoClient(config.MONGO_DB_AUTH_URL)
        daily_notices_metadata_repo = DailyNoticesMetadataRepository(mongo_client)
    notice_repo = notice_repo or NoticeRepository(daily_notices_metadata_repo.mongodb_client)

    # Generate list of dates from date range
    date_range = generate_list_of_dates_from_date_range(start_date, end_date)

    for day in date_range:
        daily_notices_metadata = daily_notices_metadata_repo.get(day)
        if not daily_notices_metadata:
            continue

        mapping_suite_packages = []
        fetched_notice_ids = []
        notice_statuses = {notice_status: 0 for notice_status in daily_notices_metadata.notice_statuses.keys()}

        for notice_id in daily_notices_metadata.ted_api_notice_ids:
            notice: Notice = notice_repo.get(notice_id)

            if notice:
                fetched_notice_ids.append(notice_id)
                notice_status = notice.status
                notice_statuses[str(notice_status)] += 1
                if notice_status >= NoticeStatus.TRANSFORMED:  # Having rdf_manifestation
                    mapping_suite_id = notice.rdf_manifestation.mapping_suite_id
                    if mapping_suite_id not in mapping_suite_packages:
                        mapping_suite_packages.append(mapping_suite_id)

        result_notice_statuses = notice_statuses.copy()
        for current_notice_status, linked_notice_statuses in NOTICE_STATUS_COVERAGE_DOWNSTREAM_TRANSITION.items():
            current_notice_status = str(current_notice_status)
            if notice_statuses[current_notice_status] > 0:
                for linked_notice_status in linked_notice_statuses:
                    result_notice_statuses[str(linked_notice_status)] += notice_statuses[current_notice_status]

        daily_notices_metadata.notice_statuses = result_notice_statuses
        daily_notices_metadata.mapping_suite_packages = mapping_suite_packages
        daily_notices_metadata.fetched_notice_ids = fetched_notice_ids
        daily_notices_metadata_repo.update(daily_notices_metadata)
