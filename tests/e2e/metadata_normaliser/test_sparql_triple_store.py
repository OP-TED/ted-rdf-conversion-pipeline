import pandas as pd

from ted_sws.metadata_normaliser.adapters.sparql_triple_store import SPARQLTripleStore


def test_sparql_triple_store():
    query = """prefix cdm: <http://publications.europa.eu/ontology/cdm#> 
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>

select * 
where 
{
 graph <http://publications.europa.eu/resource/authority/buyer-legal-type>
 {    
    ?concept dc:identifier ?code .
    #?s ?p ?o
  }
}
limit 10
"""

    execute_query = SPARQLTripleStore().with_query(
        sparql_query=query)

    tabular_results = execute_query.fetch_tabular()
    tree_results = execute_query.fetch_tree()

    assert isinstance(tabular_results, pd.DataFrame)
    assert isinstance(tree_results, dict)
    assert tree_results["results"]["bindings"][0]["concept"][
               "value"] == "http://publications.europa.eu/resource/authority/buyer-legal-type/OP_DATPRO"
