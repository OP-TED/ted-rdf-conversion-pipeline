from click.testing import CliRunner

from ted_sws.core.entrypoints.api.common import single_result_response, unescape_value
from ted_sws.core.entrypoints.api.server import api_server_start as cli_api_server_start

cmdRunner = CliRunner()


def test_single_result_response(input_value, response_type_json, response_type_raw):
    result_raw: str = single_result_response(input_value, response_type_raw)
    assert isinstance(result_raw, str)
    assert result_raw != ""

    result_json: dict = single_result_response(input_value, response_type_json)
    assert isinstance(result_json, dict)
    assert "result" in result_json
    assert result_json.get("result") != ""


def test_unescape_value(escaped_input_value, unescaped_input_value):
    assert unescape_value(escaped_input_value) == unescaped_input_value


def test_api_server():
    host = "test-localhost"
    port = -1
    response = cmdRunner.invoke(cli_api_server_start, ["--host", host, "--port", port])
    assert f"{host}:{port}" in response.output
