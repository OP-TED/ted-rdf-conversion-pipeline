from typing import Union

from pymongo import MongoClient

from ted_sws.event_manager.adapters.log import is_event_loggable
from ted_sws.event_manager.adapters.log.log_writer import LogWriter, DICT_TYPE


def log_write(title, message: str = None, request: DICT_TYPE = None,
              mongodb_client: MongoClient = None) -> Union[str, bool]:
    if not is_event_loggable():
        return False

    log_writer = LogWriter(mongodb_client)
    return log_writer.save(title, message, request)
