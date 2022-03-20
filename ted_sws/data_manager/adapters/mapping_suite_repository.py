from typing import Iterator

from ted_sws.domain.adapters.repository_abc import MappingSuiteRepositoryABC
from ted_sws.domain.model.transform import MappingSuite


class MappingSuiteRepositoryMongoDB(MappingSuiteRepositoryABC):

    def add(self, mapping_suite: MappingSuite):
        pass

    def update(self, mapping_suite: MappingSuite):
        pass

    def get(self, reference) -> MappingSuite:
        pass

    def list(self) -> Iterator[MappingSuite]:
        pass


class MappingSuiteRepositoryInFileSystem(MappingSuiteRepositoryABC):
    def add(self, mapping_suite: MappingSuite):
        pass

    def update(self, mapping_suite: MappingSuite):
        pass

    def get(self, reference) -> MappingSuite:
        pass

    def list(self) -> Iterator[MappingSuite]:
        pass