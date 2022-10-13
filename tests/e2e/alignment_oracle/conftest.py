import pytest


@pytest.fixture
def limes_sparql_endpoint() -> str:
    return "https://fuseki.ted-data.eu/test_limes/query"
