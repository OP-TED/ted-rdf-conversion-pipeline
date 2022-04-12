#!/usr/bin/python3

"""

"""

from ted_sws.core.domain.message_bus import message_bus
from ted_sws.core.model.message import Log
from ted_sws.core.adapters.logger import Logger, LoggingType, LoggerFactory


def log_message(logging_type: LoggingType) -> Log:
    str_longing_type = logging_type.value
    return Log(
        title=str_longing_type + " :: test_message_bus_log",
        messages=[str_longing_type + " :: log_message :: 1", str_longing_type + " :: log_message :: 2"]
    )


def test_message_bus_log(caplog):
    logging_type = LoggingType.PY
    log = log_message(logging_type)
    message_bus.set_domain_logger(LoggerFactory.get(logging_type, name="py-domain"))
    message_bus.handle(log)
    assert log.title in caplog.text
    for message in log.messages:
        assert message in caplog.text

    logging_type = LoggingType.ELK
    log = log_message(logging_type)
    message_bus.set_domain_logger(LoggerFactory.get(logging_type, name="elk-domain"))
    message_bus.handle(log)
    assert log.title in caplog.text
    for message in log.messages:
        assert message in caplog.text
