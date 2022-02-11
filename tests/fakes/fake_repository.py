from typing import List

from ted_sws.domain.adapters.repository_abc import NoticeRepositoryABC
from ted_sws.domain.model.notice import Notice


class FakeNoticeRepository(NoticeRepositoryABC):
    """
       This fake repository is intended for storing Notice objects.
    """

    def __init__(self):
        """

        """
        self.repository = {}

    def add(self, notice: Notice):
        """
            This method allows you to add notice objects to the repository.
        :param notice:
        :return:
        """
        self.repository[notice.ted_id] = notice

    def get(self, reference) -> Notice:
        """
            This method allows a notice to be obtained based on an identification reference.
        :param reference:
        :return:
        """
        if reference in self.repository.keys():
            return self.repository[reference]

        return None


    def list(self) -> List[str]:
        """
            This method allows all records to be retrieved from the repository.
        :return:
        """
        return list(self.repository.keys())