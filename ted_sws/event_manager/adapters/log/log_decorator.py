import inspect
from datetime import datetime, timezone
from typing import Any

from decorator import decorate
from pymongo import MongoClient

from ted_sws.event_manager.adapters.log_repository import LogRepository
from ted_sws.event_manager.adapters.log import LoggedBy
from ted_sws.event_manager.adapters.log import is_event_loggable
from ted_sws.event_manager.adapters.log.log_writer import LogWriter
from ted_sws.event_manager.model.message import DBProcessLog as Log, DBProcessLogRequest as LogRequest, \
    DBProcessLogResponse as LogResponse


# Log decorator


def log(mongodb_client: MongoClient = None, title: str = '', message: str = ''):
    def wrapper(fn):
        def get_path() -> str:
            return fn.__name__

        def get_request(args: Any, kwargs: Any) -> LogRequest:
            log_request = LogRequest()
            signature = inspect.signature(fn)
            idx = 0
            if args:
                for param in signature.parameters.values():
                    if param.kind == inspect.Parameter.VAR_POSITIONAL:
                        break
                    else:
                        log_request.POSITIONAL_OR_KEYWORD[param.name] = LogWriter.sanitize_request_param(args[idx])
                    idx += 1

                while idx < len(args):
                    log_request.VAR_POSITIONAL[str(idx)] = LogWriter.sanitize_request_param(args[idx])
                    idx += 1

            log_request.VAR_KEYWORD = LogWriter.sanitize_request_params({**kwargs})

            return log_request

        def get_response(result: Any) -> LogResponse:
            return LogWriter.get_response(result)

        def log_save_before(request: LogRequest, started_at) -> (str, Log):
            log_repo = LogRepository(mongodb_client)

            log_entry = Log()
            log_entry.title = title
            log_entry.message = message
            log_entry.path = get_path()
            log_entry.name = fn.__name__
            log_entry.request = request
            log_entry.started_at = started_at
            log_entry.logged_by = LoggedBy.DECORATOR

            return log_repo.add(log_entry), log_entry

        def log_save_after(_id: str, log_entry: Log, started_at, ended_at, result) -> str:
            log_repo = LogRepository(mongodb_client)

            log_entry.duration = (ended_at - started_at).total_seconds()
            log_entry.ended_at = ended_at
            log_entry.response = get_response(result)

            return log_repo.update(_id, log_entry)

        def process(fn, *args, **kwargs):
            if not is_event_loggable():
                return fn(*args, **kwargs)

            started_at = datetime.now(timezone.utc)
            log_request = get_request(args, kwargs)
            _id, log_entry = log_save_before(log_request, started_at)
            result = fn(*args, **kwargs)
            ended_at = datetime.now(timezone.utc)
            log_save_after(_id, log_entry, started_at, ended_at, result)

            return result

        return decorate(fn, process)

    return wrapper
