from typing import Iterator

from ted_sws.data_manager.adapters.repository_abc import NoticeRepositoryABC
from ted_sws.core.model.notice import Notice, NoticeStatus


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

    def update(self, notice: Notice):
        """
            This method allows you to update notice objects to the repository.
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

    def get_notice_by_status(self, notice_status: NoticeStatus) -> Iterator[Notice]:
        """
            This method provides all notices based on its status.
        :param notice_status:
        :return:
        """
        return [value for value in self.repository.values() if value.status == notice_status]

    def list(self) -> Iterator[Notice]:
        """
            This method allows all records to be retrieved from the repository.
        :return:
        """
        return list(self.repository.values())
