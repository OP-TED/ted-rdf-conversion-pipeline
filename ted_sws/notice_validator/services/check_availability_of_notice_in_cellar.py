from ted_sws.data_manager.adapters.sparql_endpoint import SPARQLTripleStoreEndpoint

WEBAPI_SPARQL_URL = "https://publications.europa.eu/webapi/rdf/sparql"
CELLAR_NOTICE_AVAILABILITY_QUERY = "ASK {{ VALUES ?instance {{<{notice_uri}>}} ?instance ?predicate [] . }}"
WEBAPI_SPARQL_RUN_FORMAT = "application/sparql-results+json"


def check_availability_of_notice_in_cellar(notice_uri: str, endpoint_url: str = WEBAPI_SPARQL_URL) -> bool:
    query = CELLAR_NOTICE_AVAILABILITY_QUERY.format(notice_uri=notice_uri)
    result = SPARQLTripleStoreEndpoint(
        endpoint_url=endpoint_url,
        use_env_credentials=False).with_query(sparql_query=query).fetch_tree()
    return result['boolean']
