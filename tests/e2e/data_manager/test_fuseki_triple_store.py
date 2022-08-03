from pathlib import Path

import pytest

from ted_sws import config
from ted_sws.data_manager.adapters.triple_store import FusekiAdapter, FusekiException

REPOSITORY_NAME = "unknown_repository_123456677"


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


def test_fuseki_triple_store_connection():
    triple_store = FusekiAdapter()
    response = triple_store.add_file_to_repository(Path("/home/mihai/work/meaningfy/ted-sws/tests/test_data/example.ttl"),
                                        repository_name="test1")
    print(response)
    # create repo
    # load sample data
    # get SAPRQL endpoint
    # query that the sparql endpoint is not empty (select * {?s ?p ?o} limit 10)
    # delete repo
