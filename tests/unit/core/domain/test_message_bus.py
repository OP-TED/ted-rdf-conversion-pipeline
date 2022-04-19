#!/usr/bin/python3

"""
"""

import logging

from ted_sws.core.adapters.logger import Logger
from ted_sws.core.domain.message_bus import message_bus
from ted_sws.core.model.message import Log

TEST_LOGGER = Logger(name="TEST_MESSAGE_BUS_LOGGER", level=logging.INFO)


def log_message() -> Log:
    return Log(
        title="test_message_bus_log",
        message=["log_message :: 1", "log_message :: 2"],
        logger=TEST_LOGGER
    )


def test_message_bus_log(caplog):
    log = log_message()
    message_bus.set_domain_logger(TEST_LOGGER)
    message_bus.handle(log)
    if log.title:
        assert log.title in caplog.text
    if log.message:
        for message in log.message:
            assert message in caplog.text
