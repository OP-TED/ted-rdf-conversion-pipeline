import json
import time
from datetime import date
from http import HTTPStatus
from typing import List, Generator

import requests

from ted_sws import config
from ted_sws.event_manager.services.log import log_error
from ted_sws.notice_fetcher.adapters.ted_api_abc import TedAPIAdapterABC, RequestAPI

DOCUMENTS_PER_PAGE = 100

DEFAULT_TED_API_QUERY_RESULT_SIZE = {"limit": DOCUMENTS_PER_PAGE,
                                     "page": 1,
                                     "scope": "ALL",
                                     }

DEFAULT_TED_API_QUERY_RESULT_FIELDS = {"fields": ["ND", "PD", "RN"]}

TOTAL_DOCUMENTS_NUMBER = "totalNoticeCount"
RESPONSE_RESULTS = "notices"
DOCUMENT_CONTENT = "content"
RESULT_PAGE_NUMBER = "page"
TED_API_FIELDS = "fields"
LINKS_TO_CONTENT_KEY = "links"
XML_CONTENT_KEY = "xml"
MULTIPLE_LANGUAGE_CONTENT_KEY = "MUL"
ENGLISH_LANGUAGE_CONTENT_KEY = "ENG"
DOCUMENT_NOTICE_ID_KEY = "ND"


class TedRequestAPI(RequestAPI):

    def __call__(self, api_url: str, api_query: dict) -> dict:
        """
            Method to make a post request to the API with a query (json). It will return the response body.
            :param api_url:
            :param api_query:
            :return: dict
        """

        response = requests.post(api_url, json=api_query)
        try_again_request_count = 0
        while response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            try_again_request_count += 1
            time.sleep(try_again_request_count * 0.1)
            response = requests.post(api_url, json=api_query)
            if try_again_request_count > 5:
                break
        if response.ok:
            response_content = json.loads(response.text)
            return response_content
        else:
            raise Exception(f"The TED-API call failed with: {response}")


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

        query = {"query": f"PD={wildcard_date}"}

        return self.get_by_query(query=query)

    def get_by_range_date(self, start_date: date, end_date: date) -> List[dict]:
        """
        Method to get a documents content by passing a date range
        :param start_date:
        :param end_date:
        :return:List[str]
        """

        date_filter = f"PD>={start_date.strftime('%Y%m%d')} AND PD<={end_date.strftime('%Y%m%d')}"

        query = {"query": date_filter}

        return self.get_by_query(query=query)

    def _retrieve_document_content(self, document_content: dict) -> str:
        """
        Method to retrieve a document content from the TedApi API
        :param document_content:
        :return:str '
        """
        xml_links = document_content[LINKS_TO_CONTENT_KEY][XML_CONTENT_KEY]
        if MULTIPLE_LANGUAGE_CONTENT_KEY not in xml_links.keys():
            exception_message = f"Language key {MULTIPLE_LANGUAGE_CONTENT_KEY} not found in {document_content[DOCUMENT_NOTICE_ID_KEY]}"
            log_error(exception_message)
            raise Exception(exception_message)
        xml_document_content_link = xml_links[MULTIPLE_LANGUAGE_CONTENT_KEY]
        response = requests.get(xml_document_content_link)
        try_again_request_count = 0
        while response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            try_again_request_count += 1
            time.sleep(try_again_request_count * 0.1)
            response = requests.get(xml_document_content_link)
            if try_again_request_count > 5:
                break
        if response.ok:
            return response.text
        else:
            raise Exception(f"The notice content can't be loaded!: {response}, {response.content}")

    def get_generator_by_query(self, query: dict, result_fields: dict = None, load_content: bool = True) -> Generator[
        dict, None, None]:
        """
        Method to get a documents content by passing a query to the API (json)
        :param query:
        :param result_fields:
        :param load_content:
        :return:Generator[dict]
        """
        query.update(DEFAULT_TED_API_QUERY_RESULT_SIZE)
        query.update(result_fields or DEFAULT_TED_API_QUERY_RESULT_FIELDS)
        response_body = self.request_api(api_url=self.ted_api_url, api_query=query)
        documents_number = response_body[TOTAL_DOCUMENTS_NUMBER]
        result_pages = 1 + int(documents_number) // DOCUMENTS_PER_PAGE
        documents_content = response_body[RESPONSE_RESULTS]
        if result_pages > 1:
            for page_number in range(2, result_pages + 1):
                query[RESULT_PAGE_NUMBER] = page_number
                response_body = self.request_api(api_url=self.ted_api_url, api_query=query)
                documents_content += response_body[RESPONSE_RESULTS]

            for document_content in documents_content:
                if load_content:
                    document_content[DOCUMENT_CONTENT] = self._retrieve_document_content(document_content)
                    del document_content[LINKS_TO_CONTENT_KEY]
                yield document_content
        else:
            for document_content in documents_content:
                if load_content:
                    document_content[DOCUMENT_CONTENT] = self._retrieve_document_content(document_content)
                    del document_content[LINKS_TO_CONTENT_KEY]
                yield document_content

    def get_by_query(self, query: dict, result_fields: dict = None, load_content: bool = True) -> List[dict]:
        """
        Method to get a documents content by passing a query to the API (json)
        :param query:
        :param result_fields:
        :param load_content:
        :return:List[dict]
        """
        return list(self.get_generator_by_query(query=query, result_fields=result_fields, load_content=load_content))

    def get_by_id(self, document_id: str) -> dict:
        """
        Method to get a document content by passing an ID
        :param document_id:
        :return: dict
        """

        query = {"query": f"ND={document_id}"}

        return self.get_by_query(query=query)[0]
