#!/usr/bin/python3

# __init__.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

""" """


from ted_sws.domain.model.metadata import TEDMetadata


def test_metadata():
    metadata = TEDMetadata(**{"AA": "Value here", "No_key": "Value"})
    assert metadata.AA == "Value here"
    assert "No_key" not in metadata.dict().keys()
