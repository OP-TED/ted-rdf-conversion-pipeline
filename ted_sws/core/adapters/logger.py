import abc
import enum
import logging

import logstash

from ted_sws import config


class LoggingType(enum.Enum):
    ELK = "ELK"
    PY = "PY"


DOMAIN_LOGGING_TYPES = config.LOGGING_TYPE.split(",") if config.LOGGING_TYPE is not None else [LoggingType.PY.value]
DOMAIN_LOGGING_TYPE = DOMAIN_LOGGING_TYPES[0]


class LoggerABC(abc.ABC):
    """
    This abstract class provides methods definitions and infos for available loggers
    """
    pass


class Logger(LoggerABC):
    """
    This class provides common features for available loggers
    """

    def __init__(self, name: str = __name__):
        self.name = name
        self.logger = logging.getLogger(name)
        self.level = logging.DEBUG
        self.logger.setLevel(self.level)

    def get_logger(self) -> logging.Logger:
        return self.logger

    def log(self, msg: str):
        msg = "\n" + self.name + "\n" + msg + "\n"
        self.logger.log(self.level, msg)


class LoggerFactory:
    @classmethod
    def get(cls, logging_type: LoggingType = LoggingType(DOMAIN_LOGGING_TYPE), name: str = __name__):
        """Factory Method to return the needed Logger, based on logging type/target"""
        loggers = {
            LoggingType.ELK: ELKLogger,
            LoggingType.PY: PYLogger
        }
        name = "{logging_type} :: {name}".format(logging_type=logging_type, name=name)
        return loggers[logging_type](name=name)


class ELKLogger(Logger):
    """
    LogStash (ELK) Logger
    """

    def __init__(self, name: str = 'logstash-logger'):
        super().__init__(name=name)

        host = config.ELK_HOST
        port = config.ELK_PORT
        version = config.ELK_VERSION

        self.logger.addHandler(logstash.LogstashHandler(host, port, version=version))
        # self.logger.addHandler(logstash.TCPLogstashHandler(host, port, version=version))


class PYLogger(Logger):
    """
    Python Logger
    """

    def __init__(self, name: str = __name__):
        super().__init__(name=name)


logger = LoggerFactory.get(name="domain-logging")
