import os

from ted_sws import RUN_ENV_NAME, RUN_ENV_VAL
from ted_sws.event_manager.services.log import log_write
from tests import RUN_ENV_VAL as TEST_RUN_ENV_VAL


def test_log_write(mongodb_client, notice_2016):
    os.environ[RUN_ENV_NAME] = RUN_ENV_VAL
    result = log_write("TITLE", "MESSAGE", {
        "VAR1": 1,
        "VAR2": 2,
        "NOTICE": notice_2016
    }, mongodb_client)
    assert result
    os.environ[RUN_ENV_NAME] = TEST_RUN_ENV_VAL


def test_log_write_within_test_env(mongodb_client):
    result = log_write(title="TITLE", message="MESSAGE", mongodb_client=mongodb_client)
    assert not result
