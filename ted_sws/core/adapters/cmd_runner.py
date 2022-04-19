import abc
import datetime
import logging

from ted_sws.core.adapters.logger import Logger
from ted_sws.core.domain.message_bus import message_bus
from ted_sws.core.model.message import Log


class CmdRunnerABC(abc.ABC):
    @abc.abstractmethod
    def on_begin(self):
        """
        Do before running the command
        :return:
        """

    @abc.abstractmethod
    def on_end(self):
        """
        Do after running the command
        :return:
        """


class CmdRunner(CmdRunnerABC):
    def __init__(self, name=__name__):
        self.name = name
        self.begin_time = None
        self.end_time = None
        self.logger = Logger(name=name, level=logging.INFO)
        self.logger.add_stdout_handler()

    def get_logger(self) -> Logger:
        return self.logger

    @staticmethod
    def _now() -> str:
        return str(datetime.datetime.now())

    def log(self, message: str):
        message_bus.handle(Log(message=message, name=self.name, logger=self.logger))

    def on_begin(self):
        self.begin_time = datetime.datetime.now()
        self.log("CMD :: BEGIN :: {now}".format(now=self._now()))

    def on_end(self):
        self.end_time = datetime.datetime.now()
        self.log("CMD :: END :: {now}".format(now=str(self.end_time)))
        self.log("CMD :: execution time: {time}".format(time=self.end_time - self.begin_time))
