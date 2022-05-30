from datetime import datetime
from typing import Optional, List

from ted_sws.core.model import PropertyBaseModel
from ted_sws.core.model.manifestation import RDFValidationManifestation


class SPARQLQuery(PropertyBaseModel):
    """
    Stores SPARQL query details
    """
    title: Optional[str]
    description: Optional[str]
    query: str


class SPARQLQueryResult(PropertyBaseModel):
    """
    Stores SPARQL query execution result
    """
    query: SPARQLQuery
    result: Optional[str]
    error: Optional[str]
    identifier: Optional[str]


class SPARQLTestSuiteExecution(RDFValidationManifestation):
    """
    Stores execution results for a SPARQL test suite
    """
    created: str = datetime.now().isoformat()
    sparql_test_suite_identifier: str
    mapping_suite_identifier: str
    execution_results: List[SPARQLQueryResult] = []

