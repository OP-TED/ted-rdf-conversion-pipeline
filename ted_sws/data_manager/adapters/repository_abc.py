import abc
from typing import Iterator, Optional

from ted_sws.core.model.notice import Notice
from ted_sws.core.model.transform import MappingSuite


class RepositoryABC(abc.ABC):
    """
       This class implements a common interface for all repositories.
    """


class NoticeRepositoryABC(RepositoryABC):
    """
       This repository is intended for storing Notice objects.
    """

    @abc.abstractmethod
    def add(self, notice: Notice):
        """
            This method allows you to add notice objects to the repository.
        :param notice:
        :return:
        """

    @abc.abstractmethod
    def update(self, notice: Notice):
        """
            This method allows you to update notice objects to the repository
        :param notice:
        :return:
        """

    @abc.abstractmethod
    def get(self, reference) -> Optional[Notice]:
        """
            This method allows a notice to be obtained based on an identification reference.
        :param reference:
        :return: Notice
        """

    @abc.abstractmethod
    def list(self) -> Iterator[Notice]:
        """
            This method allows all records to be retrieved from the repository.
        :return: list of notices
        """


class MappingSuiteRepositoryABC(RepositoryABC):
    """
       This repository is intended for storing MappingSuite objects.
    """

    @abc.abstractmethod
    def add(self, mapping_suite: MappingSuite):
        """
            This method allows you to add MappingSuite objects to the repository.
        :param mapping_suite:
        :return:
        """

    @abc.abstractmethod
    def update(self, mapping_suite: MappingSuite):
        """
            This method allows you to update MappingSuite objects to the repository
        :param mapping_suite:
        :return:
        """

    @abc.abstractmethod
    def get(self, reference) -> MappingSuite:
        """
            This method allows a MappingSuite to be obtained based on an identification reference.
        :param reference:
        :return: MappingSuite
        """

    @abc.abstractmethod
    def list(self) -> Iterator[MappingSuite]:
        """
            This method allows all records to be retrieved from the repository.
        :return: list of MappingSuites
        """
