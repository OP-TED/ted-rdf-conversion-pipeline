import os
from unittest import mock

import mongomock

from ted_sws import RUN_ENV_NAME, RUN_ENV_VAL
from ted_sws.event_manager.adapters.log.log_decorator import log

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


@mock.patch.dict(os.environ, {RUN_ENV_NAME: RUN_ENV_VAL})
def test_log_decorator(notice_2016, notice_2021):
    result = log_test(1, 2, notice_2016, 3, 4, k="TEST", test_notice=notice_2021)
    assert result

    result = log_test_with_dict_response(1, 2, notice_2016)
    assert isinstance(result, dict)



def test_log_decorator_within_test_env(notice_2016, notice_2021):
    result = log_test(1, 2, notice_2016, 3, 4, k="TEST", test_notice=notice_2021)
    assert result
