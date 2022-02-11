#!/usr/bin/python3

# conftest.py
# Date:  07/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """

import pytest

from tests import TEST_DATA_PATH


@pytest.fixture()
def sample_metadata():
    possible_location = TEST_DATA_PATH / "notice_packager" / "metadata.json"
    # do json load and return that
    return {"title": "no title here"}


@pytest.fixture()
def sample_rdf():
    return """...."""
