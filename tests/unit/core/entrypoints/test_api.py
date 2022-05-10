import uuid

from click.testing import CliRunner
from fastapi.testclient import TestClient

from ted_sws.core.entrypoints.api.main import api_server_start as cli_api_server_start
from ted_sws.core.entrypoints.api.main import app, single_result_response, string_md5, uuid_ns_by_type

client = TestClient(app)
cmdRunner = CliRunner()


def test_api_server():
    host = "test-localhost"
    port = -1
    response = cmdRunner.invoke(cli_api_server_start, ["--host", host, "--port", port])
    assert f"{host}:{port}" in response.output


def test_single_result_response(input_value, response_type_json, response_type_raw):
    result_raw: str = single_result_response(input_value, response_type_raw)
    assert isinstance(result_raw, str)
    assert result_raw != ""

    result_json: dict = single_result_response(input_value, response_type_json)
    assert isinstance(result_json, dict)
    assert "result" in result_json
    assert result_json.get("result") != ""


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
    response = client.get(f"/fn/md5/{input_value}?response_type={response_type_json.value}")
    assert response.status_code == 200
    result_json = response.json()
    assert "result" in result_json
    assert result_json.get("result") != ""


def test_api_fn_uuid(input_value, response_type_raw, uuid_input_process_type_md5):
    response = client.get(f"/fn/uuid/{input_value}?response_type={response_type_raw.value}&input_process_type="
                          f"{uuid_input_process_type_md5.value}")
    assert response.status_code == 200
    assert response.content != ""
