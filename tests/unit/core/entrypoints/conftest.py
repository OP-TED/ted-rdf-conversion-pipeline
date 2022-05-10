#!/usr/bin/python3

# conftest.py


""" """

import pytest

from ted_sws.core.entrypoints.api.main import ResponseType, UUIDInputProcessType, UUIDNamespaceType


@pytest.fixture()
def response_type_json() -> ResponseType:
    return ResponseType.JSON


@pytest.fixture()
def response_type_raw() -> ResponseType:
    return ResponseType.RAW


@pytest.fixture()
def input_value() -> str:
    return "F03_2014AWARD_CONTRACT1AWARDED_CONTRACT1CONTRACTORS1CONTRACTOR1"


@pytest.fixture()
def uuid_input_process_type_md5() -> UUIDInputProcessType:
    return UUIDInputProcessType.MD5


@pytest.fixture()
def uuid_namespace_type_dns() -> UUIDNamespaceType:
    return UUIDNamespaceType.DNS


@pytest.fixture()
def uuid_namespace_type_url() -> UUIDNamespaceType:
    return UUIDNamespaceType.URL


@pytest.fixture()
def uuid_namespace_type_oid() -> UUIDNamespaceType:
    return UUIDNamespaceType.OID


@pytest.fixture()
def uuid_namespace_type_x500() -> UUIDNamespaceType:
    return UUIDNamespaceType.X500
