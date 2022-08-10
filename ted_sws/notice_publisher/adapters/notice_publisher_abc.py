from abc import ABC


class NoticePublisherABC(ABC):
    def connect(self, **kwargs) -> bool:
        """

        :param kwargs:
        :return:
        """

    def publish(self, **kwargs) -> bool:
        """

        :param kwargs:
        :return:
        """

    def disconnect(self, **kwargs) -> bool:
        """

        :param kwargs:
        :return:
        """
