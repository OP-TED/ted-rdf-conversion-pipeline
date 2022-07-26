import hashlib
import uuid
from enum import Enum
from typing import Optional

from fastapi import APIRouter

from ted_sws.notice_transformer.entrypoints.api.digest_service.common import ResponseType, single_result_response, \
    unescape_value
from ted_sws.notice_transformer.entrypoints.api.digest_service.routes.xpath import sanitize_xpath

ROUTE_PREFIX = "/hashing"

route = APIRouter()


class UUIDInputProcessType(Enum):
    XPATH = "xpath"
    MD5 = "md5"
    RAW = "raw"


class UUIDNamespaceType(Enum):
    DNS = "DNS"
    URL = "URL"
    OID = "OID"
    X500 = "X500"


class UUIDVersion(Enum):
    UUID3 = "UUID3"
    UUID5 = "UUID5"


def string_md5(value: str):
    """
    Generates MD5 hash, based on provided value
    :param value:
    :return:
    """
    return hashlib.md5(value.encode('utf8')).hexdigest()


def uuid_ns_by_type(ns_type: UUIDNamespaceType) -> uuid.UUID:
    """
    Returns UUID Namespace Value to be used when generating the UUID string, based on provided Namespace Type
    :param ns_type:
    :return:
    """
    uuid_ns: uuid.UUID = uuid.NAMESPACE_DNS
    if ns_type == UUIDNamespaceType.URL:
        uuid_ns = uuid.NAMESPACE_URL
    elif ns_type == UUIDNamespaceType.OID:
        uuid_ns = uuid.NAMESPACE_OID
    elif ns_type == UUIDNamespaceType.X500:
        uuid_ns = uuid.NAMESPACE_X500
    return uuid_ns


@route.get("/fn/md5/{value:path}")
async def fn_md5(value: str, response_type: Optional[ResponseType] = ResponseType.RAW):
    """
    Returns a hash generated by the MD5 message digest algorithm, taking as arguments:
    - @value: string value to be hashed;
    - @response_type: response type/format to be returned;
    """
    value = unescape_value(value)
    result = string_md5(value)
    return single_result_response(result, response_type)


@route.get("/fn/uuid/{value:path}")
async def fn_uuid(
        value: str,
        process_type: Optional[UUIDInputProcessType] = UUIDInputProcessType.XPATH,
        version: Optional[UUIDVersion] = UUIDVersion.UUID3,
        ns_type: Optional[UUIDNamespaceType] = UUIDNamespaceType.URL,
        response_type: Optional[ResponseType] = ResponseType.RAW
):
    """
    Returns generated UUID, taking as arguments:
    - @value: string value to be hashed;
    - @process_type: algorithm used to process input @value before generating UUID string;
    - @version: UUID Version;
    - @ns_type: namespace type to be used when generating UUID string;
    - @response_type: response type/format to be returned;
    """
    value = unescape_value(value)

    if process_type == UUIDInputProcessType.XPATH:
        value = sanitize_xpath(value)
    elif process_type == UUIDInputProcessType.MD5:
        value = string_md5(value)

    uuid_ns = uuid_ns_by_type(ns_type)

    uuid_result: uuid.UUID
    if version == UUIDVersion.UUID5:
        uuid_result = uuid.uuid5(uuid_ns, value)
    else:
        uuid_result = uuid.uuid3(uuid_ns, value)

    result = str(uuid_result)
    return single_result_response(result, response_type)