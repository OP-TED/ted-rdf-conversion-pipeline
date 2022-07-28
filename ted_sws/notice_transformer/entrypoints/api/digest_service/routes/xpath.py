import re
from typing import Optional

from fastapi import APIRouter

from ted_sws.notice_transformer.entrypoints.api.digest_service.common import ResponseType, single_result_response, \
    unescape_value

ROUTE_PREFIX = "/xpath"

route = APIRouter()


def sanitize_xpath(value: str):
    """
    Sanitize/canonize the XPath value
    :param value:
    :return:
    """
    value = re.sub(r'.*?}(F\d+_\d+?)\[\d+](.*)', r'\1\2', value)
    value = re.sub(r'(\[)|(])|(/Q{.*?})', '', value)
    value = value.strip(' \n')
    return value


@route.get("/fn/canonize/{value:path}")
async def fn_canonize(value: str, response_type: Optional[ResponseType] = ResponseType.RAW):
    """
    Returns the canonical path, taking as arguments:
    - @value: xpath to be canonized;
    - @response_type: response type/format to be returned;
    """
    value = unescape_value(value)
    result = sanitize_xpath(value)
    return single_result_response(result, response_type)
