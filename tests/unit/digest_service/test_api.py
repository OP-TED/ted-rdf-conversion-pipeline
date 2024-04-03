from fastapi.responses import JSONResponse, PlainTextResponse

from ted_sws.notice_transformer.entrypoints.api.digest_service.common import single_result_response, unescape_value


def test_single_result_response(input_value, response_type_json, response_type_raw):
    response = single_result_response(input_value, response_type_raw)
    assert isinstance(response, PlainTextResponse)
    response = single_result_response(input_value, response_type_json)
    assert isinstance(response, JSONResponse)


def test_unescape_value(escaped_input_value, unescaped_input_value):
    assert unescape_value(escaped_input_value) == unescaped_input_value
