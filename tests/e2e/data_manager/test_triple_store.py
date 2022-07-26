#!/usr/bin/python3

# minio_feature_store.py
# Date:  21.07.2022
# Author: Eugeniu Costetchi
# Email: eugen@meaningfy.ws

"""

"""

REPOSITORY_NAME = "this_is_a_test_repository"
SPARQL_QUERY = "select * {?s ?p ?o} limit 10"


def test_repository_creation(allegro_triple_store):
    if REPOSITORY_NAME in allegro_triple_store.list_repositories():
        allegro_triple_store.delete_repository(repository_name=REPOSITORY_NAME)

    assert REPOSITORY_NAME not in allegro_triple_store.list_repositories()

    allegro_triple_store.create_repository(repository_name=REPOSITORY_NAME)

    assert REPOSITORY_NAME in allegro_triple_store.list_repositories()

    allegro_triple_store.delete_repository(repository_name=REPOSITORY_NAME)


def test_loading_data(allegro_triple_store, path_ttl_file):
    if REPOSITORY_NAME not in allegro_triple_store.list_repositories():
        allegro_triple_store.create_repository(repository_name=REPOSITORY_NAME)

    allegro_triple_store.add_file_to_repository(file_path=path_ttl_file, repository_name=REPOSITORY_NAME)

    sparql_endpoint = allegro_triple_store.get_sparql_triple_store_endpoint(repository_name=REPOSITORY_NAME)

    assert sparql_endpoint

    query_result = sparql_endpoint.with_query(sparql_query=SPARQL_QUERY).fetch_tree()

    assert query_result
    assert "head" in query_result
    assert "results" in query_result
    assert len(query_result["results"]["bindings"]) == 10
