#!/usr/bin/python3

# minio_feature_store.py
# Date:  21.07.2022
# Author: Eugeniu Costetchi
# Email: eugen@meaningfy.ws

"""

"""
from pathlib import Path

REPOSITORY_NAME = "this_is_a_test_repository"
SPARQL_QUERY = "select * {?s ?p ?o} limit 10"


def _triple_store_repository_creation(triple_store):
    if REPOSITORY_NAME in triple_store.list_repositories():
        triple_store.delete_repository(repository_name=REPOSITORY_NAME)

    assert REPOSITORY_NAME not in triple_store.list_repositories()

    triple_store.create_repository(repository_name=REPOSITORY_NAME)

    assert REPOSITORY_NAME in triple_store.list_repositories()

    triple_store.delete_repository(repository_name=REPOSITORY_NAME)


def _triple_store_loading_data(triple_store, path_ttl_file):
    if REPOSITORY_NAME not in triple_store.list_repositories():
        triple_store.create_repository(repository_name=REPOSITORY_NAME)

    triple_store.add_file_to_repository(file_path=path_ttl_file, repository_name=REPOSITORY_NAME)

    sparql_endpoint = triple_store.get_sparql_triple_store_endpoint(repository_name=REPOSITORY_NAME)

    assert sparql_endpoint

    query_result = sparql_endpoint.with_query(sparql_query=SPARQL_QUERY).fetch_tree()

    assert query_result
    assert "head" in query_result
    assert "results" in query_result
    assert len(query_result["results"]["bindings"]) == 10


def test_fuseki_repository_creation(fuseki_triple_store):
    _triple_store_repository_creation(fuseki_triple_store)


def test_fuseki_loading_data(fuseki_triple_store, path_ttl_file):
    _triple_store_loading_data(fuseki_triple_store, Path(path_ttl_file))


def test_allegro_repository_creation(allegro_triple_store):
    _triple_store_repository_creation(allegro_triple_store)


def test_allegro_loading_data(allegro_triple_store, path_ttl_file):
    _triple_store_loading_data(allegro_triple_store, path_ttl_file)
