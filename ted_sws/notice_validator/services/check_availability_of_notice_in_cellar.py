import time
from typing import List, Set

from pymongo import MongoClient

from ted_sws import config
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.core.service.batch_processing import chunks
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_manager.adapters.sparql_endpoint import SPARQLTripleStoreEndpoint, SPARQLStringEndpoint
from ted_sws.event_manager.services.log import log_notice_error
from ted_sws.notice_validator.resources import NOTICE_AVAILABILITY_SPARQL_QUERY_TEMPLATE_PATH, \
    NOTICES_AVAILABILITY_SPARQL_QUERY_TEMPLATE_PATH, GET_NOTICE_URI_SPARQL_QUERY_TEMPLATE_PATH

WEBAPI_SPARQL_RUN_FORMAT = "application/sparql-results+json"
INVALID_NOTICE_URI = 'https://www.w3.org/1999/02/22-rdf-syntax-ns#type-invalid'
DEFAULT_NOTICES_BATCH_SIZE = 5000
DEFAULT_CELLAR_REQUEST_DELAY = 3


def check_availability_of_notice_in_cellar(notice_uri: str, endpoint_url: str = None) -> bool:
    """
    This service checks the notice availability in Cellar
    :param notice_uri:
    :param endpoint_url:
    :return:
    """
    if not endpoint_url:
        endpoint_url = config.CELLAR_WEBAPI_SPARQL_URL
    query_template = NOTICE_AVAILABILITY_SPARQL_QUERY_TEMPLATE_PATH.read_text(encoding="utf-8")
    query = query_template.format(notice_uri=notice_uri)
    result = SPARQLTripleStoreEndpoint(endpoint_url=endpoint_url).with_query(sparql_query=query).fetch_tree()
    return result['boolean']


def check_availability_of_notices_in_cellar(notice_uries: List[str], endpoint_url: str = None) -> Set[str]:
    """
    This service check the notices availability in Cellar, and return available set of notice uries.
    :param notice_uries:
    :param endpoint_url:
    :return:
    """
    if not endpoint_url:
        endpoint_url = config.CELLAR_WEBAPI_SPARQL_URL
    query_template = NOTICES_AVAILABILITY_SPARQL_QUERY_TEMPLATE_PATH.read_text(encoding="utf-8")
    notice_uries = " ".join([f"<{notice_uri}>" for notice_uri in notice_uries])
    query = query_template.format(notice_uries=notice_uries)
    result = SPARQLTripleStoreEndpoint(endpoint_url=endpoint_url,
                                       use_post_method=True).with_query(sparql_query=query).fetch_tabular()
    return set(result['s'].to_list())


def generate_notice_uri_from_notice(notice: Notice) -> str:
    """
    This service generates Cellar URI for a notice, determined by notice_id
    :param notice:
    :return:
    """
    if notice.distilled_rdf_manifestation and notice.distilled_rdf_manifestation.object_data:
        sparql_endpoint = SPARQLStringEndpoint(rdf_content=notice.distilled_rdf_manifestation.object_data)
        sparql_query = GET_NOTICE_URI_SPARQL_QUERY_TEMPLATE_PATH.read_text(encoding="utf-8")
        notice_uries = sparql_endpoint.with_query(sparql_query=sparql_query).fetch_tabular()["s"].to_list()
        if len(notice_uries) == 1:
            return notice_uries[0]
        else:
            log_notice_error(message="Invalid extraction of notice URI from distilled RDF manifestation!",
                             notice_id=notice.ted_id)

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
            notice_uri = generate_notice_uri_from_notice(notice=notice)
        if check_availability_of_notice_in_cellar(notice_uri=notice_uri):
            notice.update_status_to(new_status=NoticeStatus.PUBLICLY_AVAILABLE)
        else:
            notice.update_status_to(new_status=NoticeStatus.PUBLICLY_UNAVAILABLE)
    return notice


def validate_notices_availability_in_cellar(notice_statuses: List[NoticeStatus], mongodb_client: MongoClient,
                                            cellar_request_delay_in_seconds: int = DEFAULT_CELLAR_REQUEST_DELAY):
    """
        This function validate availability in cellar foreach notice from notices with a notice_status in
        notice_statuses.
    :param notice_statuses:
    :param mongodb_client:
    :param cellar_request_delay_in_seconds:
    :return:
    """
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    for notice_status in notice_statuses:
        selected_notices = notice_repository.get_notices_by_status(notice_status=notice_status)
        for selected_notices_chunk in chunks(selected_notices, chunk_size=DEFAULT_NOTICES_BATCH_SIZE):
            selected_notices_map = {
                generate_notice_uri_from_notice(notice=notice): notice
                for notice in selected_notices_chunk
            }
            selected_notices_uries = list(selected_notices_map.keys())
            available_notice_uries_in_cellar = check_availability_of_notices_in_cellar(
                notice_uries=selected_notices_uries)
            for notice_uri, notice in selected_notices_map.items():
                if notice_uri in available_notice_uries_in_cellar:
                    notice.update_status_to(new_status=NoticeStatus.PUBLICLY_AVAILABLE)
                    notice.normalised_metadata.published_in_cellar_counter += 1
                else:
                    notice.update_status_to(new_status=NoticeStatus.PUBLICLY_UNAVAILABLE)
                notice_repository.update(notice=notice)
            time.sleep(cellar_request_delay_in_seconds)
