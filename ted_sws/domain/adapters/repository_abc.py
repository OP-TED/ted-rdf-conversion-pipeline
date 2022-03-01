import abc
from typing import Iterator

from ted_sws.domain.model.notice import Notice


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
    def get(self, reference) -> Notice:
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
