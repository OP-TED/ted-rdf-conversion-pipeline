#!/usr/bin/python3

import logging
from ted_sws.event_manager.adapters.log.logger import Logger

"""
"""

from ted_sws.core.adapters.cmd_runner import CmdRunner


def test_cmd_runner(caplog):
    cmd_runner = CmdRunner(name="TEST_CMD_RUNNER")
    cmd_runner.run()
    assert "CMD :: BEGIN" in caplog.text
    assert "CMD :: END" in caplog.text


def test_cmd_runner_with_logger(caplog):
    cmd_runner = CmdRunner(name="TEST_CMD_RUNNER",
                           logger=Logger(name="TEST_CMD_RUNNER_LOGGER", level=logging.INFO, logging_handlers=[]))
    cmd_runner.run()
    assert "CMD :: BEGIN" in caplog.text
    assert "CMD :: END" in caplog.text
