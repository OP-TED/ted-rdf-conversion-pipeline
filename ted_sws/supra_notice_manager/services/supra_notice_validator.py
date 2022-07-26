from datetime import datetime, date, time
from typing import Union

from pymongo import MongoClient

from ted_sws.core.model.supra_notice import SupraNoticeValidationReport, DailySupraNotice
from ted_sws.data_manager.adapters.supra_notice_repository import DailySupraNoticeRepository
from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, RequestAPI

day_type = Union[datetime, date]


def validate_and_update_daily_supra_notice(notice_publication_day: day_type, mongodb_client: MongoClient,
                                           request_api: RequestAPI = None):
    if isinstance(notice_publication_day, date):
        notice_publication_day = datetime.combine(notice_publication_day, time())

    repo = DailySupraNoticeRepository(mongodb_client=mongodb_client)
    supra_notice: DailySupraNotice = repo.get(reference=notice_publication_day)

    if not supra_notice:
        raise ValueError("SupraNotice not found in Database!")

    fetched_notice_ids_list = supra_notice.notice_ids or []
    fetched_notice_ids = set(fetched_notice_ids_list)

    ted_api_adapter: TedAPIAdapter = TedAPIAdapter(request_api=request_api)
    documents = ted_api_adapter.get_by_wildcard_date(wildcard_date=notice_publication_day.strftime("%Y%m%d*"))
    api_notice_ids_list = [document["ND"] for document in documents] if documents and len(documents) else []
    api_notice_ids = set(api_notice_ids_list)

    validation_report = SupraNoticeValidationReport(object_data="")
    missing_notice_ids = api_notice_ids - fetched_notice_ids
    if len(missing_notice_ids):
        validation_report.missing_notice_ids = missing_notice_ids

    supra_notice.validation_report = validation_report
    repo.update(daily_supra_notice=supra_notice)
