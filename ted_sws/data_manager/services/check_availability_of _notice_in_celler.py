
from ted_sws.data_manager.adapters.repository_abc import NoticeRepositoryABC
from ted_sws.data_manager.adapters.sparql_endpoint import SPARQLTripleStoreEndpoint

NOTICE_URI = 'http://publications.europa.eu/resource/celler/396207_2018'
NOTICE_ID = '982988'


def check_availability_of_notice_in_celler(notice_id, cellar_sparql_endpoint,
                                      notice_uri):
    notice_id = NOTICE_ID
    notice_uri = NOTICE_URI

    query = f"""
        ASK
    {{
	    VALUES ?{notice_id} {notice_uri}
	    ?{notice_uri} ?predicate [] .
    }}
    """
    execute_query = SPARQLTripleStoreEndpoint(endpoint_url=cellar_sparql_endpoint).with_query(sparql_query=query)
    if execute_query is True:
        print('the notice status is publicly available')
    else:
        print('the notice status is publicly unavailable')
