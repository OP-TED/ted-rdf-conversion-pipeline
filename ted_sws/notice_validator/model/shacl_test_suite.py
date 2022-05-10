from datetime import datetime
from typing import Optional, List

from ted_sws.core.model import PropertyBaseModel
from ted_sws.core.model.manifestation import RDFValidationManifestation


class SHACLShapeValidation(PropertyBaseModel):
    """
    Stores SHACL shapes details
    """
    title: Optional[str]
    content: str


class SHACLShapeValidationResult(PropertyBaseModel):
    """
    Stores SHACL shapes validation result
    """
    shapes: SHACLShapeValidation
    conforms: Optional[str]
    results_dict: Optional[dict]
    error: Optional[str]
    identifier: Optional[str]


class SHACLShapeResultReport(RDFValidationManifestation):
    """
    Stores SHACL shape execution report result
    """
    created: str = datetime.now().isoformat()
    mapping_suite_identifier: str
    validation_result: SHACLShapeValidationResult


class SHACLTestSuiteExecution(RDFValidationManifestation):
    """
    Stores execution results for a SHACL test suite
    """
    created: str = datetime.now().isoformat()
    shacl_test_suite_identifier: str
    mapping_suite_identifier: str
    execution_results: List[SHACLShapeValidationResult] = []
