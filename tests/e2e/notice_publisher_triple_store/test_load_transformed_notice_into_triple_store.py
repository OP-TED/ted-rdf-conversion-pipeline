from ted_sws.notice_publisher_triple_store.services.load_transformed_notice_into_triple_store import \
    load_notice_into_triple_store, DEFAULT_NOTICE_REPOSITORY_NAME, load_notice_into_s3_triple_store
from tests.fakes.fake_repository import FakeNoticeRepository
from ted_sws.data_manager.adapters.triple_store import S3TripleStoreAdapter, TripleStoreABC
import pytest

SPARQL_QUERY_TRIPLES = "select * {?s ?p ?o}"
SPARQL_QUERY_GRAPH = "SELECT ?g {  GRAPH ?g { ?s ?p ?o  } }"
SPARQL_QUERY_FIXED_URI = "select * { <http://data.europa.eu/a4g/resource/ReviewerOrganisationIdentifier/2018-S-175-396207/de2507f9-ae25-37c8-809c-0109efe10669> ?p ?o .} "


def _check_triple_store(triple_store: TripleStoreABC, repository_name):
    sparql_endpoint = triple_store.get_sparql_triple_store_endpoint(DEFAULT_NOTICE_REPOSITORY_NAME)
    assert sparql_endpoint is not None

    df_query_result = sparql_endpoint.with_query(sparql_query=SPARQL_QUERY_TRIPLES).fetch_tabular()
    assert df_query_result is not None
    assert len(df_query_result) > 0

    df_query_result = sparql_endpoint.with_query(sparql_query=SPARQL_QUERY_GRAPH).fetch_tree()
    assert df_query_result is not None
    assert len(df_query_result) > 0

    df_query_result = sparql_endpoint.with_query(sparql_query=SPARQL_QUERY_FIXED_URI).fetch_tabular()
    assert df_query_result is not None
    assert len(df_query_result) > 0


def test_load_notice_into_triple_store(transformed_complete_notice, allegro_triple_store):
    fake_notice_repo = FakeNoticeRepository()
    fake_notice_repo.add(transformed_complete_notice)
    load_notice_into_triple_store(notice_id=transformed_complete_notice.ted_id, notice_repository=fake_notice_repo,
                                  triple_store_repository=allegro_triple_store)

    _check_triple_store(triple_store=allegro_triple_store, repository_name=DEFAULT_NOTICE_REPOSITORY_NAME)

    with pytest.raises(ValueError):
        load_notice_into_triple_store(notice_id="invalid_notice_id", notice_repository=fake_notice_repo,
                                      triple_store_repository=allegro_triple_store)


def test_load_notice_into_s3_triple_store(transformed_complete_notice):
    fake_notice_repo = FakeNoticeRepository()
    fake_notice_repo.add(transformed_complete_notice)
    repository_name = "test_repository"
    s3_triple_store: S3TripleStoreAdapter = load_notice_into_s3_triple_store(
        notice_id=transformed_complete_notice.ted_id,
        notice_repository=fake_notice_repo,
        repository_name=repository_name)

    _check_triple_store(triple_store=s3_triple_store, repository_name=repository_name)

    s3_triple_store.delete_repository(repository_name=repository_name)
