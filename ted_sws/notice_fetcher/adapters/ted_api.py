import io
import json
import pathlib
import tarfile
import time
from collections import defaultdict
from datetime import date, datetime
from http import HTTPStatus
from io import BytesIO
from typing import List, Generator, Callable, Optional, Set

import pandas as pd
import requests
from requests import Response

from ted_sws import config
from ted_sws.event_manager.services.log import log_warning
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
META_PUBLICATION_DATE_KEY = "PD"
META_PUBLICATION_DATE_FORMATS = ["%Y-%m-%d%z", "%Y-%m-%dT%H:%M:%S%z"]
DOCUMENT_NOTICE_ID_KEY = "ND"
MAX_RETRIES = 5
DEFAULT_BACKOFF_FACTOR = 1
TED_API_OJS_REGISTER_ENDPOINT_TEMPLATE = "{endpoint}{year}"
TED_API_DAILY_BULK_ENDPOINT_TEMPLATE = "{endpoint}{year}{ojs_number:05}"
PUBLICATION_DATE_COLUMN = "Publication date "
OJS_NUMBER_COLUMN = "OJS"
OJS_REGISTER_FORMAT_DATE = "%d/%m/%Y"
CUSTOM_HEADER = {'User-Agent': 'TED-SWS-Pipeline-Fetcher'}


def execute_request_with_retries(request_lambda: Callable,
                                 max_retries: int = MAX_RETRIES,
                                 backoff_factor: float = DEFAULT_BACKOFF_FACTOR) -> Response:
    response = request_lambda()
    requests_counter = 0
    while response.status_code != HTTPStatus.OK:
        if requests_counter >= max_retries:
            log_warning(f"Max retries exceeded, retried {max_retries} times!")
            return response
        requests_counter += 1
        time_to_sleep = backoff_factor * requests_counter
        log_warning(f"Request returned status code {response.status_code}, retrying in {time_to_sleep} seconds!")
        time.sleep(time_to_sleep)
        response = request_lambda()
    return response


def convert_publication_date_to_utc_date(publication_date: str) -> date:
    publication_date.replace("Z", "+00:00")
    for date_format in META_PUBLICATION_DATE_FORMATS:
        try:
            result_date = datetime.strptime(publication_date, date_format)
            return result_date
        except:
            continue
    raise Exception(f"Could not parse publication date! Publication date: {publication_date}")


def preprocess_notice_id(notice_id: str) -> str:
    return notice_id.strip().replace("_", "-").lstrip("0")


def get_configured_custom_headers(custom_header: Optional[dict] = None) -> dict:
    headers = requests.utils.default_headers()
    if custom_header:
        headers.update(custom_header)
    return headers


def get_ojs_number_by_date(search_date: date, custom_header: Optional[dict] = None) -> Optional[int]:
    headers = get_configured_custom_headers(custom_header)
    request_url = TED_API_OJS_REGISTER_ENDPOINT_TEMPLATE.format(endpoint=config.TED_API_OJS_REGISTER_ENDPOINT,
                                                                year=search_date.year)
    response = execute_request_with_retries(lambda: requests.get(request_url, headers=headers))
    if response.status_code != HTTPStatus.OK:
        raise Exception(f"Can't get OJS number, status code: {response.status_code}, message: {response.text}")
    ojs_register_df = pd.read_csv(BytesIO(response.content))
    date_to_ojs_map = dict(zip(ojs_register_df[PUBLICATION_DATE_COLUMN].str.strip(),
                               ojs_register_df[OJS_NUMBER_COLUMN].astype(str).str.strip()))
    search_date_str = search_date.strftime(OJS_REGISTER_FORMAT_DATE)
    if search_date_str in date_to_ojs_map.keys():
        return int(date_to_ojs_map[search_date_str])
    else:
        raise Exception(f"Can't get OJS number, for search date: {search_date_str}!"
                        f"\nResponse code: {response.status_code}"
                        f"\nReason: {response.text}")


def get_notice_contents_by_date(search_date: date,
                                custom_header: Optional[dict] = None,
                                filter_notice_ids: Optional[Set[str]] = None) -> Generator:
    ojs_number = get_ojs_number_by_date(search_date=search_date, custom_header=custom_header)
    request_url = TED_API_DAILY_BULK_ENDPOINT_TEMPLATE.format(endpoint=config.TED_API_DAILY_BULK_ENDPOINT,
                                                              year=search_date.year, ojs_number=ojs_number)
    headers = get_configured_custom_headers(custom_header=custom_header)
    response = execute_request_with_retries(lambda: requests.get(request_url, headers=headers))
    if response.status_code != 200:
        raise Exception(
            f"Can't load notices content for date {search_date}, status code {response.status_code}, message {response.text}")
    with tarfile.open(fileobj=io.BytesIO(response.content), mode='r:gz') as tar_file:
        for member in tar_file.getmembers():
            try:
                notice_id = pathlib.Path(member.name).stem
                notice_id = preprocess_notice_id(notice_id)
                if filter_notice_ids:
                    if notice_id not in filter_notice_ids:
                        continue
                file = tar_file.extractfile(member=member)
                xml_content = file.read()
                yield notice_id, xml_content.decode('utf-8')
            except Exception as e:
                raise Exception(f"Notice bulk for date {search_date} is invalid!")


class TedRequestAPI(RequestAPI):

    def __call__(self, api_url: str, api_query: dict) -> dict:
        """
            Method to make a post request to the API with a query (json). It will return the response body.
            :param api_url:
            :param api_query:
            :return: dict
        """

        response = execute_request_with_retries(request_lambda=lambda: requests.post(api_url, json=api_query))
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
        self.ted_api_url = ted_api_url or config.TED_API_URL

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
        documents_meta = response_body[RESPONSE_RESULTS]
        if result_pages > 1:
            for page_number in range(2, result_pages + 1):
                query[RESULT_PAGE_NUMBER] = page_number
                response_body = self.request_api(api_url=self.ted_api_url, api_query=query)
                documents_meta += response_body[RESPONSE_RESULTS]

        if load_content:
            notices_groups_by_publication_date = defaultdict(dict)
            for document_meta in documents_meta:
                del document_meta[LINKS_TO_CONTENT_KEY]
                publication_date = convert_publication_date_to_utc_date(document_meta[META_PUBLICATION_DATE_KEY])
                notice_id = preprocess_notice_id(document_meta[DOCUMENT_NOTICE_ID_KEY])
                notices_groups_by_publication_date[publication_date][notice_id] = document_meta

            for publication_date, notices_meta in notices_groups_by_publication_date.items():
                filter_notice_ids = set(notices_meta.keys())
                notice_contents = get_notice_contents_by_date(search_date=publication_date, custom_header=CUSTOM_HEADER,
                                                              filter_notice_ids=filter_notice_ids)
                for notice_id, xml_content in notice_contents:
                    result_document_meta = notices_meta[notice_id]
                    result_document_meta[DOCUMENT_CONTENT] = xml_content
                    yield result_document_meta
        else:
            for document_meta in documents_meta:
                yield document_meta

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
