from fastapi import FastAPI

from ted_sws.notice_transformer.entrypoints.api.digest_service.routes.hashing import route as hashing_route, \
    ROUTE_PREFIX as HASHING_ROUTE_PREFIX
from ted_sws.notice_transformer.entrypoints.api.digest_service.routes.xpath import route as xpath_route, ROUTE_PREFIX as XPATH_ROUTE_PREFIX

API_VERSION = "1"

app_api = FastAPI(
    version=API_VERSION
)
app_api.include_router(hashing_route, prefix=HASHING_ROUTE_PREFIX)
app_api.include_router(xpath_route, prefix=XPATH_ROUTE_PREFIX)

API_PREFIX = "/api/v" + app_api.version

app = FastAPI()
app.mount(API_PREFIX, app_api)
