#!/usr/bin/python3

# conftest.py


""" """

import pytest
from fastapi.testclient import TestClient

from ted_sws.notice_transformer.entrypoints.api.digest_service.common import ResponseType
from ted_sws.notice_transformer.entrypoints.api.digest_service.main import app
from ted_sws.notice_transformer.entrypoints.api.digest_service.routes.hashing import UUIDInputProcessType, UUIDNamespaceType, UUIDVersion


@pytest.fixture
def api_client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def response_type_json() -> ResponseType:
    return ResponseType.JSON


@pytest.fixture
def response_type_raw() -> ResponseType:
    return ResponseType.RAW


@pytest.fixture
def input_value() -> str:
    return "F03_2014AWARD_CONTRACT1AWARDED_CONTRACT1CONTRACTORS1CONTRACTOR1"


@pytest.fixture
def escaped_input_value() -> str:
    return "TED_EXPORT%5B1%5D%2FQ%7Bhttp%3A%2F%2Fpublications.europa.eu%2Fresource%2Fschema%2Fted%2FR2.0.9%2Fpublication%7D"


@pytest.fixture
def xpath() -> str:
    return "/Q{http://publications.europa.eu/resource/schema/ted/R2.0.9/publication}TED_EXPORT[1]/Q{http://publications.europa.eu/resource/schema/ted/R2.0.9/publication}FORM_SECTION[1]/Q{http://publications.europa.eu/resource/schema/ted/R2.0.9/publication}F06_2014[1]/Q{http://publications.europa.eu/resource/schema/ted/R2.0.9/publication}AWARD_CONTRACT[1]/Q{http://publications.europa.eu/resource/schema/ted/R2.0.9/publication}AWARDED_CONTRACT[1]/Q{http://publications.europa.eu/resource/schema/ted/R2.0.9/publication}CONTRACTORS[1]/Q{http://publications.europa.eu/resource/schema/ted/R2.0.9/publication}CONTRACTOR[1]"


@pytest.fixture
def unescaped_input_value() -> str:
    return "TED_EXPORT[1]/Q{http://publications.europa.eu/resource/schema/ted/R2.0.9/publication}"


@pytest.fixture
def uuid_input_process_type_md5() -> UUIDInputProcessType:
    return UUIDInputProcessType.MD5


@pytest.fixture
def uuid_input_process_type_xpath() -> UUIDInputProcessType:
    return UUIDInputProcessType.XPATH


@pytest.fixture
def uuid_version3() -> UUIDVersion:
    return UUIDVersion.UUID3


@pytest.fixture
def uuid_version5() -> UUIDVersion:
    return UUIDVersion.UUID5


@pytest.fixture
def uuid_namespace_type_dns() -> UUIDNamespaceType:
    return UUIDNamespaceType.DNS


@pytest.fixture
def uuid_namespace_type_url() -> UUIDNamespaceType:
    return UUIDNamespaceType.URL


@pytest.fixture
def uuid_namespace_type_oid() -> UUIDNamespaceType:
    return UUIDNamespaceType.OID


@pytest.fixture
def uuid_namespace_type_x500() -> UUIDNamespaceType:
    return UUIDNamespaceType.X500
