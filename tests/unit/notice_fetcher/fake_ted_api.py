from datetime import date
from typing import List

from ted_sws.notice_fetcher.adapters.ted_api_abc import DocumentSearchABC
from tests.unit.notice_fetcher.conftest import get_xml_notice


class FakeTedDocumentSearch(DocumentSearchABC):
    def get_by_wildcard_date(self, wildcard_date: str) -> List[str]:
        return [get_xml_notice()]

    def get_by_id(self, document_id: str) -> str:
        return get_xml_notice()

    def get_by_range_date(self, start_date: date, end_date: date) -> List[str]:
        return [get_xml_notice()]

    def get_by_query(self, query: dict) -> List[str]:
        return [get_xml_notice()]
