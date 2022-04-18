import abc
import datetime


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
    def __init__(self, loggable=False):
        self.loggable = loggable
        self.begin_time = None
        self.end_time = None

    @staticmethod
    def _now() -> str:
        return str(datetime.datetime.now())

    def on_begin(self):
        self.begin_time = datetime.datetime.now()
        if self.loggable:
            print("CMD :: BEGIN :: {now}".format(now=self._now()), flush=True)

    def on_end(self):
        self.end_time = datetime.datetime.now()
        if self.loggable:
            print("CMD :: END :: {now}".format(now=str(self.end_time)), flush=True)
            print("CMD :: EXEC_TIME :: {time}".format(time=self.end_time-self.begin_time), flush=True)
