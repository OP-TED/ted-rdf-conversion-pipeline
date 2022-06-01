from ted_sws.core.model.manifestation import SPARQLQuery, SPARQLQueryResult, SPARQLTestSuiteValidationReport


def test_sparql_query(query_content):
    sparql_query = SPARQLQuery(query=query_content)
    assert "ASK" in sparql_query.query
    assert isinstance(sparql_query, SPARQLQuery)


def test_sparql_query_result(query_content):
    sparql_query = SPARQLQuery(query=query_content)
    sparql_query_result = SPARQLQueryResult(query=sparql_query, result="pass")
    assert "pass" == sparql_query_result.result
    assert isinstance(sparql_query_result, SPARQLQueryResult)
    assert "ASK" in sparql_query_result.query.query


def test_sparql_test_suite_execution(query_content):
    sparql_query = SPARQLQuery(query=query_content)
    sparql_query_result_one = SPARQLQueryResult(query=sparql_query, result="pass")
    sparql_query_result_two = SPARQLQueryResult(query=sparql_query, result="fail")
    execution_results = [sparql_query_result_one, sparql_query_result_two]
    test_suite_execution = SPARQLTestSuiteValidationReport(test_suite_identifier="cool",
                                                           mapping_suite_identifier="awesome",
                                                           object_data="RDFValidationManifestation here",
                                                           validation_results=execution_results
                                                           )
    assert test_suite_execution.created
    assert isinstance(test_suite_execution, SPARQLTestSuiteValidationReport)
    assert len(test_suite_execution.validation_results) == 2
