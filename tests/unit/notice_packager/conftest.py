#!/usr/bin/python3

# conftest.py
# Date:  07/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """

import pytest


@pytest.fixture()
def sample_metadata():
    return {}


@pytest.fixture()
def sample_rdf():
    return """...."""
