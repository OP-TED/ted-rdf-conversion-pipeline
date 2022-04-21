#!/usr/bin/python3

"""
"""

from ted_sws.core.adapters.cmd_runner import CmdRunner


def test_cmd_runner(caplog):
    cmd_runner = CmdRunner(name="TEST_CMD_RUNNER")
    cmd_runner.run()
    assert "CMD :: BEGIN" in caplog.text
    assert "CMD :: END" in caplog.text
