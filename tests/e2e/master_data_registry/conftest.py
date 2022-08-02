from string import Template

import pytest


@pytest.fixture
def triple_store_endpoint_url() -> str:
    return "https://agraph.staging.ted-data.eu/repositories/package_f03"


@pytest.fixture
def get_all_organisation_sparql_query() -> str:
    return """
prefix org: <http://www.w3.org/ns/org#>
prefix epo: <http://data.europa.eu/a4g/ontology#>
SELECT ?s
{
  ?s a epo:Organisation .
}
    """


@pytest.fixture
def get_all_triples_by_uri_sparql_query() -> Template:
    return Template("""
prefix org: <http://www.w3.org/ns/org#>
prefix epo: <http://data.europa.eu/a4g/ontology#>
select ?s ?p ?o 
{
  values ?s {<$uri>}
  ?s ?p ?o .                                                                                                              
}
    """)
