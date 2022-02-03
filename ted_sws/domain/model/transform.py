#!/usr/bin/python3

# transform.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import abc


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


