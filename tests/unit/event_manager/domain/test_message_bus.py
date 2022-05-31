#!/usr/bin/python3

"""
"""

import logging

from ted_sws.event_manager.adapters.log.logger import Logger
from ted_sws.event_manager.domain.message_bus import message_bus
from ted_sws.event_manager.model.message import Log

TEST_LOGGER = Logger(name="TEST_MESSAGE_BUS_LOGGER", level=logging.INFO, logging_handlers=[])


def test_message_bus_log(caplog):
    log1 = Log(
        title="test_message_bus_log",
        message=["log_message1 :: 1", "log_message :: 2"],
        logger=TEST_LOGGER
    )
    message_bus.handle(log1)

    log2 = Log(
        message="log_message2 :: MESSAGE",
        logger=TEST_LOGGER
    )
    message_bus.handle(log2)

    log3 = Log(
        message=["log_message3 :: 1", "log_message3 :: 2"],
        logger=TEST_LOGGER
    )
    message_bus.handle(log3)

    if log1.title:
        assert log1.title in caplog.text
    if log1.message:
        for message in log1.message:
            assert message in caplog.text

    if log2.message:
        assert log2.message in caplog.text

    if log3.message:
        for message in log3.message:
            assert message in caplog.text
