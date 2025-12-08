from typing import List
from ted_sws.core.model.notice import NoticeStatus

NOTICE_STATUS = "status"
FORM_NUMBER = "normalised_metadata.form_number"
XSD_VERSION = "normalised_metadata.xsd_version"
PUBLICATION_DATE = "normalised_metadata.publication_date"


def build_selector_mongodb_filter(notice_statuses: List[str], form_number: str = None,
                                  start_date: str = None, end_date: str = None,
                                  xsd_version: str = None) -> dict:
    """

    :param notice_statuses:
    :param form_number:
    :param start_date:
    :param end_date:
    :param xsd_version:
    :return:
    """
    from datetime import datetime
    mongodb_filter = {NOTICE_STATUS: {"$in": notice_statuses}}
    if form_number:
        mongodb_filter[FORM_NUMBER] = form_number
    if start_date and end_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        mongodb_filter[PUBLICATION_DATE] = {'$gte': start_date, '$lte': end_date}
    if xsd_version:
        mongodb_filter[XSD_VERSION] = xsd_version
    return mongodb_filter


def notice_ids_selector_by_status(notice_statuses: List[NoticeStatus], form_number: str = None,
                                  start_date: str = None, end_date: str = None,
                                  xsd_version: str = None) -> List[str]:
    """

    :param notice_statuses:
    :param form_number:
    :param start_date:
    :param end_date:
    :param xsd_version:
    :return:
    """
    from pymongo import MongoClient
    from ted_sws import config
    from ted_sws.data_manager.adapters.notice_repository import NoticeRepository, NOTICE_TED_ID

    mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice_statuses = [str(notice_status) for notice_status in notice_statuses]
    mongodb_filter = build_selector_mongodb_filter(notice_statuses=notice_statuses,
                                                   form_number=form_number,
                                                   start_date=start_date,
                                                   end_date=end_date,
                                                   xsd_version=xsd_version)
    mongodb_result_iterator = notice_repository.collection.find(mongodb_filter, {NOTICE_TED_ID: 1})
    return [result_dict[NOTICE_TED_ID] for result_dict in mongodb_result_iterator]
