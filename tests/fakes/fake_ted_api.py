import copy
import json
from datetime import date
from typing import List

from ted_sws.notice_fetcher.adapters.ted_api_abc import TedAPIAdapterABC, RequestAPI
from tests import TEST_DATA_PATH


def get_fake_api_response() -> dict:
    path = TEST_DATA_PATH / "notices" / "2021-OJS237-623049.json"
    return json.loads(path.read_text())


class FakeRequestAPI(RequestAPI):
    """

    """

    def __call__(self, api_url: str, api_query: dict) -> dict:
        """

        :param api_url:
        :param api_query:
        :return:
        """
        return copy.deepcopy(get_fake_api_response())


class FakeTedApiAdapter(TedAPIAdapterABC):
    """

    """

    def get_by_wildcard_date(self, wildcard_date: str) -> List[dict]:
        """

        :param wildcard_date:
        :return:
        """
        return [notice_data for notice_data in get_fake_api_response()["results"]]

    def get_by_id(self, document_id: str) -> dict:
        """

        :param document_id:
        :return:
        """
        return get_fake_api_response()["results"][0]

    def get_by_range_date(self, start_date: date, end_date: date) -> List[dict]:
        """

        :param start_date:
        :param end_date:
        :return:
        """
        return [notice_data for notice_data in get_fake_api_response()["results"]]

    def get_by_query(self, query: dict, result_fields: dict = None) -> List[dict]:
        """

        :param query:
        :param result_fields:
        :return:
        """
        return [notice_data for notice_data in get_fake_api_response()["results"]]
