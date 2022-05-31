import abc


class LoggerABC:
    """
    This abstract class provides methods definitions and infos for available loggers
    """

    @abc.abstractmethod
    def log(self, record, level):
        """
            This method allows you to add log objects to the repository.
        :return:
        """
