import base64
import copy
from datetime import date
from typing import List

from ted_sws.notice_fetcher.adapters.ted_api_abc import DocumentSearchABC, RequestAPI
from tests.unit.notice_fetcher.conftest import get_api_response

FAKE_RESPONSE = {
    "took": 90,
    "total": 1,
    "results": [
        {
            "AA": "8",
            "AC": "2",
            "CY": "DE",
            "DI": "2009/81/EC",
            "DS": "2022-02-02",
            "MA": "D",
            "NC": "4",
            "ND": "067623-2022",
            "content": base64.b64encode("content here".encode('utf-8'))
        }
    ]
}


class FakeRequestAPI(RequestAPI):
    """

    """

    def __call__(self, api_url: str, api_query: dict) -> dict:
        """

        :param args:
        :param kwargs:
        :return:
        """
        return copy.deepcopy(FAKE_RESPONSE)

class FakeTedDocumentSearch(DocumentSearchABC):
    """

    """

    def get_by_wildcard_date(self, wildcard_date: str) -> List[dict]:
        """

        :param wildcard_date:
        :return:
        """
        return [get_api_response()]

    def get_by_id(self, document_id: str) -> dict:
        """

        :param document_id:
        :return:
        """
        return get_api_response()

    def get_by_range_date(self, start_date: date, end_date: date) -> List[dict]:
        """

        :param start_date:
        :param end_date:
        :return:
        """
        return [get_api_response()]

    def get_by_query(self, query: dict) -> List[dict]:
        """

        :param query:
        :return:
        """
        return [get_api_response()]
