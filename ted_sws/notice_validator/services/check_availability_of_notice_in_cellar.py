from pymongo import MongoClient

from ted_sws import config
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_manager.adapters.sparql_endpoint import SPARQLTripleStoreEndpoint

WEBAPI_SPARQL_URL = "https://publications.europa.eu/webapi/rdf/sparql"
CELLAR_NOTICE_AVAILABILITY_QUERY = "ASK {{ VALUES ?instance {{<{notice_uri}>}} ?instance ?predicate [] . }}"
WEBAPI_SPARQL_RUN_FORMAT = "application/sparql-results+json"


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
    return 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type-invalid'


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


def validate_and_update_notice_availability_in_cellar_by_id(notice_id: str, mongodb_client: MongoClient,
                                                            notice_uri: str = None) -> Notice:
    """
    This service checks the notice, identified by notice_id, availability in Cellar
    and update the database with correspondingly updated notice
    :param notice_id:
    :param notice_uri:
    :param mongodb_client:
    :return:
    """
    notice_repository: NoticeRepository = NoticeRepository(mongodb_client=mongodb_client)
    notice: Notice = notice_repository.get(reference=notice_id)
    if not notice:
        raise ValueError(f"Notice({notice_id}) was not found in the database!")

    return validate_and_update_notice_availability_in_cellar(notice=notice, notice_uri=notice_uri,
                                                             mongodb_client=mongodb_client)


def validate_and_update_notice_availability_in_cellar(notice: Notice, mongodb_client: MongoClient,
                                                      notice_uri: str = None) -> Notice:
    """
    This service checks the notice availability in Cellar
    and update the database with correspondingly updated notice.
    Only PUBLISHED notices are checked for availability in Cellar.
    If a notice is available in Cellar, than the status will be changed to PUBLICLY_AVAILABLE,
    otherwise to PUBLICLY_UNAVAILABLE.
    Service updates only notices that have PUBLICLY_UNAVAILABLE status, as check for PUBLICLY_AVAILABLE notices
    is not needed anymore.
    :param notice:
    :param notice_uri:
    :param mongodb_client:
    :return:
    """
    old_notice_status = notice.status
    notice = validate_notice_availability_in_cellar(notice=notice, notice_uri=notice_uri)
    if notice.status != old_notice_status:
        notice_repository: NoticeRepository = NoticeRepository(mongodb_client=mongodb_client)
        notice_repository.update(notice=notice)
    return notice
