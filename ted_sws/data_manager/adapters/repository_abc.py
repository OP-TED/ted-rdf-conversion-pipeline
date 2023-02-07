import abc
from typing import Iterator, Optional

from ted_sws.core.model.manifestation import Manifestation
from ted_sws.core.model.metadata import Metadata
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.supra_notice import DailySupraNotice
from ted_sws.core.model.transform import MappingSuite


class RepositoryABC(abc.ABC):
    """
       This class implements a common interface for all repositories.
    """


class MetadataRepositoryABC(RepositoryABC):
    """
       This repository is intended for storing Metadata objects.
    """

    @abc.abstractmethod
    def add(self, reference: str, metadata: Metadata):
        """
            This method allows you to add metadata objects to the repository.
        :param reference:
        :param metadata:
        :return:
        """

    @abc.abstractmethod
    def update(self, reference: str, metadata: Metadata):
        """
            This method allows you to update metadata objects to the repository
        :param reference:
        :param metadata:
        :return:
        """

    @abc.abstractmethod
    def get(self, reference: str) -> Optional[Metadata]:
        """
            This method allows a metadata to be obtained based on an identification reference.
        :param reference:
        :return: Metadata
        """

    @abc.abstractmethod
    def remove(self, reference: str):
        """
            This method remove a metadata based on an identification reference.
        :param reference:
        :return:
        """

class ManifestationRepositoryABC(RepositoryABC):
    """
       This repository is intended for storing Manifestation objects.
    """

    @abc.abstractmethod
    def add(self, reference: str, manifestation: Manifestation):
        """
            This method allows you to add manifestation objects to the repository.
        :param reference:
        :param manifestation:
        :return:
        """

    @abc.abstractmethod
    def update(self, reference: str, manifestation: Manifestation):
        """
            This method allows you to update manifestation objects to the repository
        :param reference:
        :param manifestation:
        :return:
        """

    @abc.abstractmethod
    def get(self, reference: str) -> Optional[Manifestation]:
        """
            This method allows a manifestation to be obtained based on an identification reference.
        :param reference:
        :return: Manifestation
        """

    @abc.abstractmethod
    def remove(self, reference: str):
        """
            This method remove a manifestation based on an identification reference.
        :param reference:
        :return:
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


class DailySupraNoticeRepositoryABC(RepositoryABC):
    """
       This repository is intended for storing DailySupraNotice objects.
    """

    @abc.abstractmethod
    def add(self, daily_supra_notice: DailySupraNotice):
        """
            This method allows you to add DailySupraNotice objects to the repository.
        :param daily_supra_notice:
        :return:
        """

    @abc.abstractmethod
    def update(self, daily_supra_notice: DailySupraNotice):
        """
            This method allows you to update DailySupraNotice objects to the repository
        :param daily_supra_notice:
        :return:
        """

    @abc.abstractmethod
    def get(self, reference) -> DailySupraNotice:
        """
            This method allows a DailySupraNotice to be obtained based on an identification reference.
        :param reference:
        :return: DailySupraNotice
        """

    @abc.abstractmethod
    def list(self) -> Iterator[DailySupraNotice]:
        """
            This method allows all records to be retrieved from the repository.
        :return: list of DailySupraNotice
        """
