from datetime import datetime
from typing import Optional, List

from ted_sws.core.model import PropertyBaseModel
from ted_sws.core.model.manifestation import RDFValidationManifestation


class QueriedSHACLShapeValidationResult(PropertyBaseModel):
    """
    Queried SHACL Validation Report which contains the following variables
    ?focusNode ?message ?resultPath ?resultSeverity ?sourceConstraintComponent ?sourceShape ?value
    """
    conforms: Optional[str]
    results_dict: Optional[dict]
    error: Optional[str]
    identifier: Optional[str]


class SHACLSuiteValidationReport(RDFValidationManifestation):
    """
    This is validation report for a SHACL test suite that contains json and html representation
    """
    created: str = datetime.now().isoformat()
    shacl_test_suite_identifier: str
    mapping_suite_identifier: str
    validation_result: QueriedSHACLShapeValidationResult

