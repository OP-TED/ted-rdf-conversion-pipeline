from click.testing import CliRunner
from fastapi.responses import JSONResponse, PlainTextResponse

from ted_sws.core.entrypoints.api.common import single_result_response, unescape_value
from ted_sws.core.entrypoints.api.server import api_server_start as cli_api_server_start

cmdRunner = CliRunner()


def test_single_result_response(input_value, response_type_json, response_type_raw):
    response = single_result_response(input_value, response_type_raw)
    assert isinstance(response, PlainTextResponse)
    response = single_result_response(input_value, response_type_json)
    assert isinstance(response, JSONResponse)


def test_unescape_value(escaped_input_value, unescaped_input_value):
    assert unescape_value(escaped_input_value) == unescaped_input_value


def test_api_server():
    host = "test-localhost"
    port = -1
    response = cmdRunner.invoke(cli_api_server_start, ["--host", host, "--port", port])
    assert f"{host}:{port}" in response.output
