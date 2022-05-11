import urllib.parse
from enum import Enum
from typing import Union


class ResponseType(Enum):
    JSON = "json"
    RAW = "raw"


def unescape_value(escaped_value: str) -> str:
    return urllib.parse.unquote(escaped_value)


def single_result_response(result: str, response_type: ResponseType) -> Union[str, dict]:
    """
    Returns RAW or JSON response, based on requested response_type
    :param result:
    :param response_type:
    :return:
    """
    if response_type == ResponseType.JSON:
        return {"result": result}
    else:
        return result
