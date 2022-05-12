import urllib.parse

from ted_sws.id_manager.entrypoints.api.main import API_PREFIX
from ted_sws.id_manager.entrypoints.api.routes.xpath import sanitize_xpath, ROUTE_PREFIX

URL_PREFIX = API_PREFIX + ROUTE_PREFIX


def test_sanitize_xpath(xpath):
    assert sanitize_xpath(xpath) == "F06_2014AWARD_CONTRACT1AWARDED_CONTRACT1CONTRACTORS1CONTRACTOR1"


def test_api_fn_canonize(api_client, xpath):
    response = api_client.get(f"{URL_PREFIX}/fn/canonize/{urllib.parse.quote(xpath, safe='')}")
    assert response.status_code == 200
    assert response.content != ""
