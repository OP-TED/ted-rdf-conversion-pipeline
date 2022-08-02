from SPARQLWrapper import XML, CSV, RDF

from ted_sws.data_manager.adapters.sparql_endpoint import SPARQLTripleStoreEndpoint


def test_triple_store_endpoint(triple_store_endpoint_url, get_all_organisation_sparql_query, get_all_triples_by_uri_sparql_query):
    triple_store = SPARQLTripleStoreEndpoint(endpoint_url=triple_store_endpoint_url)
    triple_store.with_query(sparql_query=get_all_organisation_sparql_query)
    org_uris = triple_store.fetch_tabular()
    for org_uri in org_uris["s"].tolist()[:2]:
        triple_store.with_query(sparql_query=get_all_triples_by_uri_sparql_query.substitute(uri=org_uri))
        org_all_triples = triple_store.fetch_tabular()
        print(org_all_triples.to_markdown())

def test_triple_store_endpoint_with_construct_sparql_query(triple_store_endpoint_url):
    query = """
prefix org: <http://www.w3.org/ns/org#>
prefix epo: <http://data.europa.eu/a4g/ontology#>

construct { 
  ?s ?p ?o .
  ?o ?op ?oo . }
{
  values ?s <$uri>
  ?s ?p ?o .
  ?o ?op ?oo .                                                                                                                
}
    """
    triple_store = SPARQLTripleStoreEndpoint(endpoint_url=triple_store_endpoint_url)
    triple_store.with_query(sparql_query=query)
    triple_store.endpoint.setReturnFormat(RDF)
    query_result = triple_store.endpoint.queryAndConvert()
    print(list(query_result.triples((None, None, None)))[0])