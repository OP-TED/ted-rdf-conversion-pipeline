from ted_sws.notice_validator.adapters.sparql_runner import SPARQLRunner


def test_sparql_runner(query_content,rdf_file_content):
    sparql_runner = SPARQLRunner(rdf_content=rdf_file_content)
    query_result = sparql_runner.query(query_object=query_content)

    assert query_result.askAnswer is False

