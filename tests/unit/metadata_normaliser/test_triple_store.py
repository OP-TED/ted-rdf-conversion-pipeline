import pandas as pd

from tests.fakes.fake_triple_store import FakeTripleStore


def test_triple_store():
    triple_store = FakeTripleStore()
    tmp_store = triple_store.with_query(sparql_query="Use SPARQL query")
    assert type(tmp_store) == FakeTripleStore
    assert tmp_store == triple_store
    tmp_df = tmp_store.fetch_tabular()
    assert tmp_df is not None
    assert isinstance(tmp_df, pd.DataFrame)
    result_dict_format = tmp_store.fetch_tree()
    assert isinstance(result_dict_format, dict)
