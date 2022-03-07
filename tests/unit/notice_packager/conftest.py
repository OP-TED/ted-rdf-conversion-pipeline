#!/usr/bin/python3

# conftest.py
# Date:  07/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """

import pytest

from tests import TEST_DATA_PATH
import json


@pytest.fixture()
def sample_metadata():
    return json.load((TEST_DATA_PATH / "notice_packager" / "metadata_template.json").open())


@pytest.fixture()
def sample_notice(sample_metadata):
    return sample_metadata["notice"]


@pytest.fixture()
def sample_work(sample_metadata):
    return sample_metadata["work"]


@pytest.fixture()
def sample_expression(sample_metadata):
    return sample_metadata["expression"]


@pytest.fixture()
def sample_manifestation(sample_metadata):
    return sample_metadata["manifestation"]
