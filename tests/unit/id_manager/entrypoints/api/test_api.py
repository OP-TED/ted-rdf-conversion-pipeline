from fastapi.responses import JSONResponse, PlainTextResponse

from ted_sws.id_manager.entrypoints.api.common import single_result_response, unescape_value
from ted_sws.id_manager.entrypoints.api.server import api_server_start as cli_api_server_start


def test_single_result_response(input_value, response_type_json, response_type_raw):
    response = single_result_response(input_value, response_type_raw)
    assert isinstance(response, PlainTextResponse)
    response = single_result_response(input_value, response_type_json)
    assert isinstance(response, JSONResponse)


def test_unescape_value(escaped_input_value, unescaped_input_value):
    assert unescape_value(escaped_input_value) == unescaped_input_value


def test_api_server(cli_runner):
    host = "test-localhost"
    port = -1
    response = cli_runner.invoke(cli_api_server_start, ["--host", host, "--port", port])
    assert f"{host}:{port}" in response.output
