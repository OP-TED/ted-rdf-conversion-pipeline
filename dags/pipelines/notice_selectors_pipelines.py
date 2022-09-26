from typing import List

from pymongo import MongoClient

from ted_sws import config
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository


def notice_ids_selector_by_status(notice_statuses: List[NoticeStatus]) -> List[str]:
    mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice_ids = []
    for notice_status in notice_statuses:
        notice_ids.extend(list(notice_repository.get_notice_ids_by_status(notice_status=notice_status)))

    return notice_ids
