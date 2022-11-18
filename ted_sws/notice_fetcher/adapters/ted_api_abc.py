import abc
from datetime import date
from typing import List


class RequestAPI(abc.ABC):
    """
      This class is an abstract interface for requests to an API
    """

    @abc.abstractmethod
    def __call__(self, api_url: str, api_query: dict) -> dict:
        """
            Method to make a post request to the API with a query (json). It will return the response body.
            :param api_url:
            :param api_query:
            :return: dict
        """


class TedAPIAdapterABC(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, document_id: str) -> dict:
        """
        Method to get a document content by ID
        :param document_id:
        :return:
        """

    @abc.abstractmethod
    def get_by_range_date(self, start_date: date, end_date: date) -> List[dict]:
        """
        Method to get a documents content by passing a date range
        :param start_date:
        :param end_date:
        :return:
        """

    @abc.abstractmethod
    def get_by_wildcard_date(self, wildcard_date: str) -> List[dict]:
        """
        Method to get a documents content by passing a wildcard date
        :param wildcard_date:
        :return:
        """

    @abc.abstractmethod
    def get_by_query(self, query: dict, result_fields: dict = None) -> List[dict]:
        """
        Method to get a documents content by passing a search query
        :param query:
        :param result_fields:
        :return:
        """
