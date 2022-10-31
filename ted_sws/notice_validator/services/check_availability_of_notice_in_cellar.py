from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.data_manager.adapters.sparql_endpoint import SPARQLTripleStoreEndpoint

WEBAPI_SPARQL_URL = "https://publications.europa.eu/webapi/rdf/sparql"
CELLAR_NOTICE_AVAILABILITY_QUERY = "ASK {{ VALUES ?instance {{<{notice_uri}>}} ?instance ?predicate [] . }}"
WEBAPI_SPARQL_RUN_FORMAT = "application/sparql-results+json"


def check_availability_of_notice_in_cellar(notice_uri: str, endpoint_url: str = WEBAPI_SPARQL_URL) -> bool:
    query = CELLAR_NOTICE_AVAILABILITY_QUERY.format(notice_uri=notice_uri)
    result = SPARQLTripleStoreEndpoint(endpoint_url=endpoint_url).with_query(sparql_query=query).fetch_tree()
    return result['boolean']


def generate_notice_uri_from_notice_id(notice_id: str) -> str:
    # TODO: implement notice_uri logic
    notice_id = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type-invalid'
    return notice_id


def validate_notice_availability_in_cellar(notice: Notice, notice_uri: str = None) -> Notice:
    if notice.status == NoticeStatus.PUBLISHED:
        if not notice_uri:
            notice_uri = generate_notice_uri_from_notice_id(notice_id=notice.ted_id)
        if check_availability_of_notice_in_cellar(notice_uri=notice_uri):
            notice.update_status_to(new_status=NoticeStatus.PUBLICLY_AVAILABLE)
        else:
            notice.update_status_to(new_status=NoticeStatus.PUBLICLY_UNAVAILABLE)
    return notice
