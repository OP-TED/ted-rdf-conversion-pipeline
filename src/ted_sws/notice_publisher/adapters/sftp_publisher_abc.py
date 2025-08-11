import abc


class SFTPPublisherABC(abc.ABC):

    @abc.abstractmethod
    def connect(self):
        """

        """

    @abc.abstractmethod
    def publish(self, source_path, remote_path):
        """

        """

    def disconnect(self):
        """

        """
