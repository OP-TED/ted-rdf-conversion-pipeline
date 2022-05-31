#!/usr/bin/python3

# manifestation.py
# Date:  03/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from datetime import datetime
from enum import Enum
from typing import List, Union, Optional

from pydantic import Field

from ted_sws.core.model import PropertyBaseModel


class ManifestationMimeType(Enum):
    """
    MIME types for manifestations used in this application
    """
    METS = "application/zip"
    XML = "application/xml"
    RDF = "application/rdf+xml"
    TURTLE = "text/turtle"


class Manifestation(PropertyBaseModel):
    """
        A manifestation that embodies a FRBR Work/Expression.
    """

    class Config:
        validate_assignment = True
        orm_mode = True

    object_data: str = Field(..., allow_mutation=True)

    def __str__(self):
        STR_LEN = 150  # constant
        content = self.object_data if self.object_data else ""
        return f"/{str(content)[:STR_LEN]}" + ("..." if len(content) > STR_LEN else "") + "/"


class XMLManifestation(Manifestation):
    """
        Original XML Notice manifestation as published on the TED website.
    """


class METSManifestation(Manifestation):
    """

    """


class RDFValidationManifestation(Manifestation):
    """
        The validation report
    """
    created: str = datetime.now().isoformat()
    test_suite_identifier: str
    mapping_suite_identifier: str


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


class SPARQLTestSuiteValidationReport(RDFValidationManifestation):
    """
    Stores execution results for a SPARQL test suite
    """
    validation_results: Union[List[SPARQLQueryResult], str]


class QueriedSHACLShapeValidationResult(PropertyBaseModel):
    """
    Queried SHACL Validation Report which contains the following variables
    ?focusNode ?message ?resultPath ?resultSeverity ?sourceConstraintComponent ?sourceShape ?value
    """
    conforms: Optional[str]
    results_dict: Optional[dict]
    error: Optional[str]
    identifier: Optional[str]


class SHACLTestSuiteValidationReport(RDFValidationManifestation):
    """
    This is validation report for a SHACL test suite that contains json and html representation
    """
    validation_results: Union[QueriedSHACLShapeValidationResult, str]


class RDFManifestation(Manifestation):
    """
        Transformed manifestation in RDF format
    """
    shacl_validations: List[SHACLTestSuiteValidationReport] = []
    sparql_validations: List[SPARQLTestSuiteValidationReport] = []

    def add_validation(self, validation: Union[SPARQLTestSuiteValidationReport, SHACLTestSuiteValidationReport]):
        if type(validation) == SHACLTestSuiteValidationReport:
            shacl_validation: SHACLTestSuiteValidationReport = validation
            if shacl_validation not in self.shacl_validations:
                self.shacl_validations.append(shacl_validation)
        elif type(validation) == SPARQLTestSuiteValidationReport:
            sparql_validation: SPARQLTestSuiteValidationReport = validation
            if sparql_validation not in self.sparql_validations:
                self.sparql_validations.append(sparql_validation)

    def is_validated(self) -> bool:
        if len(self.shacl_validations) and len(self.sparql_validations):
            return True
        return False
