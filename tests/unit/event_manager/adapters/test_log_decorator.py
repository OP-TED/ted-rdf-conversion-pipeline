from ted_sws.event_manager.adapters.log.log_decorator import log
import mongomock
import os
from ted_sws import RUN_ENV_NAME, RUN_ENV_VAL
from tests import RUN_ENV_VAL as TEST_RUN_ENV_VAL

mongo_client = mongomock.MongoClient()


@log(mongo_client)
def log_test(arg1, arg2, notice, *args, **kwargs):
    return True


@log(mongo_client)
def log_test_with_dict_response(arg1, arg2, notice):
    return {
        "ARG1": arg1,
        "ARG2": arg2,
        "NOTICE": notice
    }


def test_log_decorator(notice_2016, notice_2021):
    os.environ[RUN_ENV_NAME] = RUN_ENV_VAL
    result = log_test(1, 2, notice_2016, 3, 4, k="TEST", test_notice=notice_2021)
    assert result

    result = log_test_with_dict_response(1, 2, notice_2016)
    assert isinstance(result, dict)

    os.environ[RUN_ENV_NAME] = TEST_RUN_ENV_VAL


def test_log_decorator_within_test_env(notice_2016, notice_2021):
    result = log_test(1, 2, notice_2016, 3, 4, k="TEST", test_notice=notice_2021)
    assert result
