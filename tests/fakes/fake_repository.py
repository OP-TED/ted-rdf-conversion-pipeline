from typing import List

from ted_sws.domain.adapters.repository_abc import NoticeRepositoryABC
from ted_sws.domain.model.notice import Notice


class FakeNoticeRepository(NoticeRepositoryABC):
    """

    """

    def __init__(self):
        """

        """
        self.repository = {}

    def add(self, notice: Notice):
        """

        :param notice:
        :return:
        """
        self.repository[notice.ted_id] = notice

    def get(self, reference) -> Notice:
        """

        :param reference:
        :return:
        """
        if reference in self.repository.keys():
            return self.repository[reference]

        return None


    def list(self) -> List[Notice]:
        """

        :return:
        """
        return [self.repository.values()]