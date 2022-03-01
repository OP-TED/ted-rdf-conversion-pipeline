import abc
from datetime import date

from ted_sws.domain.adapters.repository_abc import NoticeRepositoryABC
from ted_sws.domain.model.manifestation import XMLManifestation
from ted_sws.domain.model.metadata import TEDMetadata
from ted_sws.domain.model.notice import Notice
from ted_sws.notice_fetcher.adapters.ted_api_abc import TedAPIAdapterABC


class NoticeFetcherABC(abc.ABC):
    """
        Abstract class for notice fetcher functionality
    """

    @abc.abstractmethod
    def fetch_notice_by_id(self, document_id: str):
        """
            This method will fetch a notice by id
        :param document_id:
        :return:
        """

    @abc.abstractmethod
    def fetch_notices_by_query(self, query: dict):
        """
            This method will fetch a list of notices by using a search query
        :param query:
        :return:
        """

    @abc.abstractmethod
    def fetch_notices_by_date_range(self, start_date: date, end_date: date):
        """
            This method will fetch a list of notices by using a date range
        :param start_date:
        :param end_date:
        :return:
        """

    @abc.abstractmethod
    def fetch_notices_by_date_wild_card(self, wildcard_date: str):
        """
            This method will fetch a list of notices by using a wildcard date
        :param wildcard_date:
        :return:
        """


class NoticeFetcher(NoticeFetcherABC):
    """
        This class will fetch notices
    """

    def __init__(self, notice_repository: NoticeRepositoryABC, ted_api_adapter: TedAPIAdapterABC):
        """

        :type notice_repository
        :param ted_api_adapter:
        """
        self.ted_api_adapter = ted_api_adapter
        self.notice_repository = notice_repository

    def _create_notice(self, notice_data: dict) -> Notice:
        """
            This method creates a Notice object
        :param notice_data:
        :return:
        """
        xml_manifestation = XMLManifestation(object_data=notice_data["content"])

        del notice_data["content"]
        ted_id = notice_data["ND"]
        original_metadata = TEDMetadata(**notice_data)

        return Notice(ted_id=ted_id, xml_manifestation=xml_manifestation, original_metadata=original_metadata)

    def fetch_notice_by_id(self, document_id):
        """
            This method will fetch a notice by id
        :param document_id:
        :return:
        """
        document_result = self.ted_api_adapter.get_by_id(document_id=document_id)
        self.notice_repository.add(notice=self._create_notice(notice_data=document_result))

    def fetch_notices_by_query(self, query: dict):
        """
            This method will fetch a list of notices by using a search query
        :param query:
        :return:
        """
        documents = self.ted_api_adapter.get_by_query(query=query)
        for document in documents:
            self.notice_repository.add(notice=self._create_notice(notice_data=document))

    def fetch_notices_by_date_range(self, start_date: date, end_date: date):
        """
            This method will fetch a list of notices by using a date range
        :param start_date:
        :param end_date:
        :return:
        """
        documents = self.ted_api_adapter.get_by_range_date(start_date=start_date, end_date=end_date)
        for document in documents:
            self.notice_repository.add(notice=self._create_notice(notice_data=document))

    def fetch_notices_by_date_wild_card(self, wildcard_date: str):
        """
            This method will fetch a list of notices by using a wildcard date
        :param wildcard_date:
        :return:
        """
        documents = self.ted_api_adapter.get_by_wildcard_date(wildcard_date=wildcard_date)
        for document in documents:
            self.notice_repository.add(notice=self._create_notice(notice_data=document))
