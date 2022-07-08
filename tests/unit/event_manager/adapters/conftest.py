import pytest
from ted_sws.event_manager.model.message import DBProcessLog, DICT_TYPE


@pytest.fixture
def db_process_log_dict() -> DICT_TYPE:
    log_dict = {
        'name': "TEST",
        'message': "TEST_LOG",
        'request': {
            'POSITIONAL_OR_KEYWORD': {
                'arg1': 1,
                'arg2': 2
            }
        },
        'duration': 12
    }

    return log_dict


@pytest.fixture
def db_process_log(db_process_log_dict) -> DBProcessLog:
    return DBProcessLog(**db_process_log_dict)
