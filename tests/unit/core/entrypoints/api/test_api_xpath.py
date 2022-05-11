import urllib.parse

from fastapi.testclient import TestClient

from ted_sws.core.entrypoints.api.main import app, API_PREFIX
from ted_sws.core.entrypoints.api.routes.xpath import sanitize_xpath, ROUTE_PREFIX

URL_PREFIX = API_PREFIX + ROUTE_PREFIX

client = TestClient(app)


def test_sanitize_xpath(xpath):
    assert sanitize_xpath(xpath) == "F06_2014AWARD_CONTRACT1AWARDED_CONTRACT1CONTRACTORS1CONTRACTOR1"


def test_api_fn_canonize(xpath):
    response = client.get(f"{URL_PREFIX}/fn/canonize/{urllib.parse.quote(xpath, safe='')}")
    assert response.status_code == 200
    assert response.content != ""
