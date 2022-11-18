from typing import List

from pymongo import MongoClient
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_manager.adapters.sparql_endpoint import SPARQLTripleStoreEndpoint

WEBAPI_SPARQL_URL = "https://publications.europa.eu/webapi/rdf/sparql"
CELLAR_NOTICE_AVAILABILITY_QUERY = "ASK {{ VALUES ?instance {{<{notice_uri}>}} ?instance ?predicate [] . }}"
WEBAPI_SPARQL_RUN_FORMAT = "application/sparql-results+json"
INVALID_NOTICE_URI = 'https://www.w3.org/1999/02/22-rdf-syntax-ns#type-invalid'


def check_availability_of_notice_in_cellar(notice_uri: str, endpoint_url: str = WEBAPI_SPARQL_URL) -> bool:
    """
    This service checks the notice availability in Cellar
    :param notice_uri:
    :param endpoint_url:
    :return:
    """
    query = CELLAR_NOTICE_AVAILABILITY_QUERY.format(notice_uri=notice_uri)
    result = SPARQLTripleStoreEndpoint(endpoint_url=endpoint_url).with_query(sparql_query=query).fetch_tree()
    return result['boolean']


def generate_notice_uri_from_notice_id(notice_id: str) -> str:
    """
    This service generates Cellar URI for a notice, determined by notice_id
    :param notice_id:
    :return:
    """
    # TODO: implement notice_uri logic
    return INVALID_NOTICE_URI


def validate_notice_availability_in_cellar(notice: Notice, notice_uri: str = None) -> Notice:
    """
    This service checks the notice availability in Cellar and returns the correspondingly updated notice
    :param notice:
    :param notice_uri:
    :return:
    """
    if notice.status in [NoticeStatus.PUBLISHED, NoticeStatus.PUBLICLY_UNAVAILABLE]:
        if not notice_uri:
            notice_uri = generate_notice_uri_from_notice_id(notice_id=notice.ted_id)
        if check_availability_of_notice_in_cellar(notice_uri=notice_uri):
            notice.update_status_to(new_status=NoticeStatus.PUBLICLY_AVAILABLE)
        else:
            notice.update_status_to(new_status=NoticeStatus.PUBLICLY_UNAVAILABLE)
    return notice


def validate_notices_availability_in_cellar(notice_statuses: List[NoticeStatus], mongodb_client: MongoClient):
    """
        This function validate availability in cellar foreach notice from notices with a notice_status in notice_statuses.
    :param notice_statuses:
    :param mongodb_client:
    :return:
    """
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    for notice_status in notice_statuses:
        selected_notices = notice_repository.get_notices_by_status(notice_status=notice_status)
        for selected_notice in selected_notices:
            validate_notice_availability_in_cellar(notice=selected_notice)
            notice_repository.update(notice=selected_notice)
