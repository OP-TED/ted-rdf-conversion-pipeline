#!/usr/bin/python3

# __init__.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

""" """
from deepdiff import DeepDiff

from ted_sws.domain.model.metadata import TEDMetadata


def test_metadata():
    metadata = TEDMetadata(**{"AA": "Value here", "No_key": "Value"})
    assert metadata.AA == "Value here"
    assert "No_key" not in metadata.dict().keys()


def test_dict_comparison():
    a1 = {'a': 1, 'a2': 1, "b": 2, "c": 3}
    a2 = {'a': 1, 'a2': 1, "b": 2, "c": 3}
    b = {'a': 1, "b": 2, "c": 3}
    c = {'d': 1, "e": 2, "c": 3}

    d1 = DeepDiff(a1, a2)
    d2 = DeepDiff(a1, b)
    d3 = DeepDiff(a1, c)

    assert not d1
    assert d2
    assert d3


def test_metadata_equality():
    md1 = TEDMetadata(**{"AA": "Value here", "No_key": "Value"})
    md2 = TEDMetadata(**{"AA": "Value here", })
    md3 = TEDMetadata(**{"AA": "Value ", "AC": "Value ", })

    assert md1 == md2
    assert md1 != md3
    assert md2 != md3
