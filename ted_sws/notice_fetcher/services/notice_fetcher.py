import abc
from datetime import date
from typing import List

from ted_sws.domain.model.manifestation import XMLManifestation
from ted_sws.domain.model.metadata import TEDMetadata
from ted_sws.domain.model.notice import Notice
from ted_sws.notice_fetcher.adapters.ted_api import TedDocumentSearch


class NoticeFetcherABC(abc.ABC):
    @abc.abstractmethod
    def get_notice_by_id(self, document_id: str) -> Notice:
        """

        :param document_id:
        :return:
        """

    @abc.abstractmethod
    def get_notices_by_query(self, query: dict) -> List[Notice]:
        """

        :param query:
        :return:
        """

    @abc.abstractmethod
    def get_notices_by_date_range(self, start_date: date, end_date: date) -> List[Notice]:
        """

        :param start_date:
        :param end_date:
        :return:
        """

    @abc.abstractmethod
    def get_notices_by_date_wild_card(self, wildcard_date: str) -> List[Notice]:
        """

        :param wildcard_date:
        :return:
        """


class NoticeFetcher(NoticeFetcherABC):
    """

    """

    def __create_notice(self, notice_data: dict) -> Notice:
        """

        :param notice_data:
        :return:
        """
        xml_manifestation = XMLManifestation(object_data=notice_data["content"])

        del notice_data["content"]
        ted_id = notice_data["ND"]
        original_metadata = TEDMetadata(**notice_data)

        return Notice(ted_id=ted_id, xml_manifestation=xml_manifestation, original_metadata=original_metadata)

    def get_notice_by_id(self, document_id):
        """

        :param document_id:
        :return:
        """
        document_result = TedDocumentSearch().get_by_id(document_id=document_id)

        return self.__create_notice(notice_data=document_result)

    def get_notices_by_query(self, query: dict) -> List[Notice]:
        """

        :param query:
        :return:
        """
        documents = TedDocumentSearch().get_by_query(query=query)
        return [self.__create_notice(notice_data=document) for document in documents]

    def get_notices_by_date_range(self, start_date: date, end_date: date) -> List[Notice]:
        """

        :param start_date:
        :param end_date:
        :return:
        """
        documents = TedDocumentSearch().get_by_range_date(start_date=start_date, end_date=end_date)
        return [self.__create_notice(notice_data=document) for document in documents]

    def get_notices_by_date_wild_card(self, wildcard_date: str) -> List[Notice]:
        """

        :param wildcard_date:
        :return:
        """
        documents = TedDocumentSearch().get_by_wildcard_date(wildcard_date=wildcard_date)
        return [self.__create_notice(notice_data=document) for document in documents]
