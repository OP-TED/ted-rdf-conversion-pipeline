import abc
import datetime
import os
import sys
from pathlib import Path
from typing import List

from ordered_set import OrderedSet

from ted_sws.data_manager.adapters.mapping_suite_repository import MS_METADATA_FILE_NAME
from ted_sws.data_manager.services.mapping_suite_resource_manager import mapping_suite_skipped_notice
from ted_sws.event_manager.adapters.event_handler import EventWriterToFileHandler, EventWriterToConsoleHandler, \
    EventWriterToMongoDBHandler
from ted_sws.event_manager.adapters.event_logger import EventLogger
from ted_sws.event_manager.adapters.log import SeverityLevelType, LOG_ERROR_TEXT, LOG_SUCCESS_TEXT, LOG_WARN_TEXT
from ted_sws.event_manager.model.event_message import EventMessage, EventMessageLogSettings
from ted_sws.event_manager.services.logger_from_context import get_cli_logger

DEFAULT_MAPPINGS_PATH = 'mappings'
DEFAULT_OUTPUT_PATH = 'output'
EXIT_CODE_OK = 0  # os.EX_OK
DEFAULT_EXIT_CODE = EXIT_CODE_OK


class CmdRunnerABC(abc.ABC):
    @abc.abstractmethod
    def on_begin(self):
        """
        Do before running the command
        :return:
        """

    @abc.abstractmethod
    def run(self):
        """
        Wrapper for running the command
        :return:
        """

    @abc.abstractmethod
    def run_cmd(self):
        """
        Run the command
        :return:
        """

    @abc.abstractmethod
    def on_end(self):
        """
        Do after running the command
        :return:
        """


class CmdRunner(CmdRunnerABC):
    def __init__(self, name=__name__, logger: EventLogger = None):
        self.name = name
        self.begin_time = None
        self.end_time = None
        self.exit_code = DEFAULT_EXIT_CODE

        if logger is None:
            logger = get_cli_logger(name=name)

        self.logger = logger

    @classmethod
    def _init_list_input_opts_split(cls, input_val: List[str]) -> List:
        input_list = []
        if input_val and len(input_val) > 0:
            for item in input_val:
                input_list += map(lambda x: x.strip(), item.split(","))
        return input_list

    @classmethod
    def _init_list_input_opts(cls, input_val: List[str]) -> List:
        """
        This method takes command line arguments (with multiple values), each element of which can have
        comma separated values and generate a list from all the values, also removing duplicates.
        Example: for "--input=value2,value1 --input=value3,value1", the method will return [value2, value1, value3]
        :param input_val:
        :return: a list of unified, deduplicated, input values
        """
        input_set = OrderedSet()
        if input_val and len(input_val) > 0:
            for item in input_val:
                input_set |= OrderedSet(map(lambda x: x.strip(), item.split(",")))
        return list(input_set)

    def get_logger(self) -> EventLogger:
        return self.logger

    @staticmethod
    def _now() -> str:
        return str(datetime.datetime.now())

    def log(self, message: str, severity_level: SeverityLevelType = SeverityLevelType.INFO):
        self.logger.log(severity_level, EventMessage(**{"message": message}),
                        handler_type=EventWriterToConsoleHandler,
                        settings=EventMessageLogSettings(briefly=True))

        self.logger.log(severity_level,
                        EventMessage(**{"message": message, "caller_name": __name__ + "." + self.name}),
                        handler_type=[EventWriterToFileHandler, EventWriterToMongoDBHandler])

    def log_failed_error(self, error: Exception):
        self.log(LOG_ERROR_TEXT.format("FAILED"))
        self.log(LOG_ERROR_TEXT.format("FAILED" + ' :: ' + type(error).__name__ + ' :: ' + str(error)))

    def log_failed_msg(self, msg: str = None):
        self.log(LOG_ERROR_TEXT.format('FAILED') + (' :: ' + msg if msg is not None else ""))

    def log_success_msg(self, msg: str = None):
        self.log(LOG_SUCCESS_TEXT.format("DONE"))
        self.log(LOG_SUCCESS_TEXT.format('SUCCESS') + (' :: ' + msg if msg is not None else ""))

    def on_begin(self):
        self.begin_time = datetime.datetime.now()
        self.log("CMD :: BEGIN :: {now}".format(now=self._now()))

    def run(self):
        self.on_begin()
        result = self.run_cmd()
        self.on_end()
        return result

    def run_cmd(self):
        """

        :return:
        """

    def run_cmd_result(self, error: Exception = None, msg: str = None, errmsg: str = None) -> bool:
        if error:
            self.log_failed_error(error)
            if errmsg is not None:
                self.log_failed_msg(errmsg)
            return False
        else:
            self.log_success_msg(msg)
            return True

    def on_end(self):
        self.end_time = datetime.datetime.now()
        self.log("CMD :: END :: {now} :: [{time}]".format(
            now=str(self.end_time),
            time=self.end_time - self.begin_time
        ))
        self.exit(self.exit_code)

    @classmethod
    def exit(cls, exit_code=DEFAULT_EXIT_CODE):
        if exit_code > EXIT_CODE_OK:
            sys.exit(exit_code)


class CmdRunnerForMappingSuite(CmdRunner):
    repository_path: Path
    mapping_suite_id: str
    notice_ids: List[str]

    def is_mapping_suite(self, suite_id):
        suite_path = self.repository_path / Path(suite_id)
        return os.path.isdir(suite_path) and any(f == MS_METADATA_FILE_NAME for f in os.listdir(suite_path))

    def skip_notice(self, notice_id: str) -> bool:
        return mapping_suite_skipped_notice(notice_id, self.notice_ids)

    def on_begin(self):
        super().on_begin()
        if hasattr(self, "mapping_suite_id") and self.mapping_suite_id:
            self.log(LOG_WARN_TEXT.format("MappingSuite: ") + self.mapping_suite_id)
        if hasattr(self, "notice_ids") and self.notice_ids:
            self.log(LOG_WARN_TEXT.format("Notices: ") + str(self.notice_ids))
