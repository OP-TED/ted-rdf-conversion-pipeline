from pathlib import Path

import pytest

from ted_sws import config
from ted_sws.data_manager.adapters.triple_store import FusekiAdapter, FusekiException
from tests import TEST_DATA_PATH
from tests.fakes.fake_repository import FakeNoticeRepository

REPOSITORY_NAME = "unknown_repository_123456677"
SPARQL_QUERY_TRIPLES = "select * {?s ?p ?o} limit 10"


def test_fuseki_triple_store_connection():
    triple_store = FusekiAdapter()
    if REPOSITORY_NAME in triple_store.list_repositories():
        triple_store.delete_repository(repository_name=REPOSITORY_NAME)

    triple_store.create_repository(repository_name=REPOSITORY_NAME)

    assert REPOSITORY_NAME in triple_store.list_repositories()

    with pytest.raises(FusekiException):
        triple_store.create_repository(repository_name=REPOSITORY_NAME)

    triple_store.delete_repository(repository_name=REPOSITORY_NAME)

    with pytest.raises(FusekiException):
        triple_store.delete_repository(repository_name=REPOSITORY_NAME)

    assert REPOSITORY_NAME not in triple_store.list_repositories()


def test_fuseki_triple_store_add_file_to_repository():
    triple_store = FusekiAdapter()
    rdf_file_path = TEST_DATA_PATH / "example.ttl"
    assert rdf_file_path.exists()
    triple_store.add_file_to_repository(rdf_file_path,
                                        repository_name="test1")


def test_fuseki_triple_store_get_sparql_endpoint(fuseki_triple_store):
    sparql_endpoint = fuseki_triple_store.get_sparql_triple_store_endpoint(repository_name="test1")
    assert sparql_endpoint is not None
    df_query_result = sparql_endpoint.with_query(sparql_query=SPARQL_QUERY_TRIPLES).fetch_tabular()
    assert df_query_result is not None
    if len(df_query_result) > 0:
        assert True
