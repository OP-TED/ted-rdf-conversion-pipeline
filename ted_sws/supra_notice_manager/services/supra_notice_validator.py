from datetime import datetime, date, time
from typing import Union

from pymongo import MongoClient

from ted_sws.core.model.manifestation import ValidationSummaryReport
from ted_sws.core.model.supra_notice import SupraNoticeValidationReport, DailySupraNotice
from ted_sws.data_manager.adapters.supra_notice_repository import DailySupraNoticeRepository
from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter, RequestAPI, TedRequestAPI
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.notice_validator.services.validation_summary_runner import generate_validation_summary_report_notices
from typing import List
from ted_sws.notice_validator.services.check_availability_of_notice_in_cellar import \
    validate_notice_availability_in_cellar

day_type = Union[datetime, date]


def validate_and_update_daily_supra_notice(notice_publication_day: day_type, mongodb_client: MongoClient,
                                           request_api: RequestAPI = None):
    if request_api is None:
        request_api = TedRequestAPI()

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

    validation_report = supra_notice.validation_report or SupraNoticeValidationReport(object_data="")
    missing_notice_ids = api_notice_ids - fetched_notice_ids
    if len(missing_notice_ids):
        validation_report.missing_notice_ids = missing_notice_ids

    supra_notice.validation_report = validation_report
    repo.update(daily_supra_notice=supra_notice)


def summary_validation_for_daily_supra_notice(notice_publication_day: day_type, mongodb_client: MongoClient):
    if isinstance(notice_publication_day, date):
        notice_publication_day = datetime.combine(notice_publication_day, time())

    repo = DailySupraNoticeRepository(mongodb_client=mongodb_client)
    supra_notice: DailySupraNotice = repo.get(reference=notice_publication_day)

    if not supra_notice:
        raise ValueError("SupraNotice not found in Database!")

    notice_repository: NoticeRepository = NoticeRepository(mongodb_client=mongodb_client)
    notices: List[Notice] = []

    for notice_id in supra_notice.notice_ids:
        notice: Notice = notice_repository.get(reference=notice_id)
        if notice:
            notices.append(notice)

    supra_notice.validation_summary = generate_validation_summary_report_notices(notices)
    # no notice_ids needed to be stored for supra_notice
    # supra_notice.validation_summary.notice_ids = []
    repo.update(daily_supra_notice=supra_notice)


def validate_and_update_supra_notice_availability_in_cellar(notice_publication_day: day_type,
                                                            mongodb_client: MongoClient):
    if isinstance(notice_publication_day, date):
        notice_publication_day = datetime.combine(notice_publication_day, time())

    repo = DailySupraNoticeRepository(mongodb_client=mongodb_client)
    supra_notice: DailySupraNotice = repo.get(reference=notice_publication_day)

    if not supra_notice:
        raise ValueError("SupraNotice not found in Database!")

    if supra_notice:
        not_published_notice_ids: List[str] = []
        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        for notice_id in supra_notice.notice_ids:
            notice = notice_repository.get(reference=notice_id)
            if notice:
                old_notice_status = notice.status
                notice._status = NoticeStatus.PUBLISHED
                notice = validate_notice_availability_in_cellar(notice=notice)
                if notice.status == NoticeStatus.PUBLICLY_UNAVAILABLE:
                    not_published_notice_ids.append(notice_id)
                if notice.status != old_notice_status:
                    notice_repository.update(notice=notice)

        validation_report = supra_notice.validation_report or SupraNoticeValidationReport(object_data="")
        validation_report.not_published_notice_ids = not_published_notice_ids
        supra_notice.validation_report = validation_report
        repo.update(daily_supra_notice=supra_notice)
