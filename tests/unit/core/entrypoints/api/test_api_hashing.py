import uuid

from fastapi.testclient import TestClient

from ted_sws.core.entrypoints.api.main import app, API_PREFIX
from ted_sws.core.entrypoints.api.routes.hashing import string_md5, uuid_ns_by_type, ROUTE_PREFIX

URL_PREFIX = API_PREFIX + ROUTE_PREFIX

client = TestClient(app)


def test_string_md5(input_value):
    result: str = string_md5(input_value)
    assert result != ""


def test_uuid_ns_by_type(uuid_namespace_type_dns, uuid_namespace_type_url, uuid_namespace_type_oid,
                         uuid_namespace_type_x500):
    result: uuid.UUID = uuid_ns_by_type(uuid_namespace_type_dns)
    assert result == uuid.NAMESPACE_DNS
    result: uuid.UUID = uuid_ns_by_type(uuid_namespace_type_url)
    assert result == uuid.NAMESPACE_URL
    result: uuid.UUID = uuid_ns_by_type(uuid_namespace_type_oid)
    assert result == uuid.NAMESPACE_OID
    result: uuid.UUID = uuid_ns_by_type(uuid_namespace_type_x500)
    assert result == uuid.NAMESPACE_X500


def test_api_fn_md5(input_value, response_type_json):
    response = client.get(f"{URL_PREFIX}/fn/md5/{input_value}?response_type={response_type_json.value}")
    assert response.status_code == 200
    result_json = response.json()
    assert "result" in result_json
    assert result_json.get("result") != ""


def test_api_fn_uuid(input_value, response_type_raw, response_type_json, uuid_input_process_type_md5, uuid_version5):
    response = client.get(f"{URL_PREFIX}/fn/uuid/{input_value}")
    assert response.status_code == 200
    assert response.content != ""

    response = client.get(
        f"{URL_PREFIX}/fn/uuid/{input_value}?process_type={uuid_input_process_type_md5.value}&response_type={response_type_raw.value}"
    )
    assert response.status_code == 200
    assert response.content != ""

    response = client.get(
        f"{URL_PREFIX}/fn/uuid/{input_value}?version={uuid_version5.value}&response_type={response_type_json.value}"
    )
    assert response.status_code == 200
    assert response.content != ""
