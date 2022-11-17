import base64
import json
from datetime import date
from typing import List

import requests

from ted_sws import config
from ted_sws.notice_fetcher.adapters.ted_api_abc import TedAPIAdapterABC, RequestAPI

DEFAULT_TED_API_QUERY_RESULT_SIZE = {"pageSize": 100,
                                     "pageNum": 1,
                                     "scope": 3
                                     }

DEFAULT_TED_API_QUERY_RESULT_FIELDS = {"fields": ["AA", "AC", "CY", "DD", "DI", "DS", "TVL", "TY",
                                                  "DT", "MA", "NC", "ND", "OC", "OJ", "OL", "OY",
                                                  "PC", "PD", "PR", "RC", "RN", "RP", "TD", "TVH",
                                                  "CONTENT", "notice-type", "award-criterion-type", "corporate-body",
                                                  "funding", "notice-identifier", "notice-version"
                                                  ]}

TOTAL_DOCUMENTS_NUMBER = "total"
RESPONSE_RESULTS = "results"
DOCUMENT_CONTENT = "content"
RESULT_PAGE_NUMBER = "pageNum"
TED_API_FIELDS = "fields"


class TedRequestAPI(RequestAPI):

    def __call__(self, api_url: str, api_query: dict) -> dict:
        """
            Method to make a post request to the API with a query (json). It will return the response body.
            :param api_url:
            :param api_query:
            :return: dict
        """

        response = requests.get(api_url, params=api_query)
        if response.ok:
            response_content = json.loads(response.text)
            return response_content
        else:
            raise Exception(f"The API call failed with: {response}")


class TedAPIAdapter(TedAPIAdapterABC):
    """
    This class will fetch documents content
    """

    def __init__(self, request_api: RequestAPI, ted_api_url: str = None):
        """
        The constructor will take the API url as a parameter
        :param request_api:
        :param ted_api_url:
        """

        self.request_api = request_api
        self.ted_api_url = ted_api_url if ted_api_url else config.TED_API_URL

    def get_by_wildcard_date(self, wildcard_date: str) -> List[dict]:
        """
        Method to get a documents content by passing a wildcard date
        :param wildcard_date:
        :return: List[str]
        """

        query = {"q": f"PD=[{wildcard_date}]"}

        return self.get_by_query(query=query)

    def get_by_range_date(self, start_date: date, end_date: date) -> List[dict]:
        """
        Method to get a documents content by passing a date range
        :param start_date:
        :param end_date:
        :return:List[str]
        """

        date_filter = f">={start_date.strftime('%Y%m%d')} AND <={end_date.strftime('%Y%m%d')}"

        query = {"q": f"PD=[{date_filter}]"}

        return self.get_by_query(query=query)

    def get_by_query(self, query: dict, result_fields: dict = None) -> List[dict]:
        """
        Method to get a documents content by passing a query to the API (json)
        :param query:
        :param result_fields:
        :return:List[str]
        """
        query.update(DEFAULT_TED_API_QUERY_RESULT_SIZE)
        query.update(result_fields or DEFAULT_TED_API_QUERY_RESULT_FIELDS)
        response_body = self.request_api(api_url=self.ted_api_url, api_query=query)

        documents_number = response_body[TOTAL_DOCUMENTS_NUMBER]
        result_pages = 1 + int(documents_number) // 100
        documents_content = response_body[RESPONSE_RESULTS]

        for page_number in range(2, result_pages + 1):
            query[RESULT_PAGE_NUMBER] = page_number
            response_body = self.request_api(api_url=self.ted_api_url, api_query=query)
            documents_content += response_body[RESPONSE_RESULTS]
        if DOCUMENT_CONTENT in query[TED_API_FIELDS]:
            decoded_documents_content = []
            for document_content in documents_content:
                document_content[DOCUMENT_CONTENT] = base64.b64decode(document_content[DOCUMENT_CONTENT]).decode(
                    encoding="utf-8")
                decoded_documents_content.append(document_content)
            return decoded_documents_content
        else:
            return documents_content

    def get_by_id(self, document_id: str) -> dict:
        """
        Method to get a document content by passing an ID
        :param document_id:
        :return: str
        """

        query = {"q": f"ND=[{document_id}]"}

        return self.get_by_query(query=query)[0]
