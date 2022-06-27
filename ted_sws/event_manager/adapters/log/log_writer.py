from datetime import datetime, timezone
from typing import Any, Dict

from pymongo import MongoClient

from ted_sws.core.model import PropertyBaseModel
from ted_sws.data_manager.adapters.log_repository import LogRepository
from ted_sws.event_manager.adapters.log import LoggedBy
from ted_sws.event_manager.model.message import DBProcessLog as Log, DBProcessLogResponse as LogResponse, DICT_TYPE
from ted_sws.core.model.notice import Notice

NOTICE_LARGE_FIELDS = ['xml_manifestation', 'rdf_manifestation', 'mets_manifestation', 'distilled_rdf_manifestation',
                       'preprocessed_xml_manifestation']


class LogWriter:
    _instance = None

    def __new__(cls, mongodb_client: MongoClient = None):
        if cls._instance is None:
            cls.log_repo = LogRepository(mongodb_client)
            cls._instance = super(LogWriter, cls).__new__(cls)

        return cls._instance

    @classmethod
    def sanitize_notice_param(cls, notice: Any) -> Any:
        for large_field in NOTICE_LARGE_FIELDS:
            if large_field in notice:
                del notice[large_field]

        return notice

    @classmethod
    def sanitize_request_param(cls, param: Any) -> Any:
        if isinstance(param, PropertyBaseModel):
            s_param = param.dict()

            # remove large fields from Notice param
            if isinstance(param, Notice):
                s_param = cls.sanitize_notice_param(s_param)
        else:
            s_param = str(param)

        return s_param

    @classmethod
    def sanitize_request_params(cls, params: Dict) -> DICT_TYPE:
        if not params:
            return None

        for key in params:
            param = params[key]
            params[key] = cls.sanitize_request_param(param)

        return params

    @classmethod
    def get_response(cls, result: Any) -> LogResponse:
        log_response = LogResponse()
        log_response.RESULT = result
        return log_response

    def save(self, title: str = None, message: str = None, request: DICT_TYPE = None) -> str:
        started_at = datetime.now(timezone.utc)
        log_entry = Log()
        log_entry.title = title
        log_entry.message = message
        log_entry.path = __name__
        log_entry.name = __name__
        log_entry.request = self.sanitize_request_params(request)
        log_entry.started_at = started_at
        log_entry.ended_at = started_at
        log_entry.response = self.get_response(True)
        log_entry.logged_by = LoggedBy.WRITER

        return self.log_repo.add(log_entry)
