#!/usr/bin/python3

# transform.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import abc
from typing import List, Optional


class FileResource:
    file_name: str
    file_content: str

class MetadataConstraints:
    pass

class TransformationRuleSet:
    resources : List[FileResource]
    rml_mapping_rules: List[FileResource]

class SHACLTestSuite:
    shacl_tests: List[FileResource]

class SPARQLTestSuite:
    purpose: Optional[str]
    sparql_tests: List[FileResource]



class MappingSuite:
    pass


class RuleSet(abc.ABC):
    """
        A set of rules used in a normalisation or transformation operation.
    """
    version: str = "0.0.1"


class TransformationRuleSet(RuleSet):
    """

    """


class NormalisationRuleSet(RuleSet):
    """

    """


