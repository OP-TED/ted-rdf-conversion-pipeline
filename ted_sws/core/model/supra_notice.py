#!/usr/bin/python3

# supra_notice.py
# Date:  16/07/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" This module implements aggregates over groups of notices and the appropriate business needs, on those groups """
import abc
from datetime import datetime, date
from typing import List, Optional

from pydantic import computed_field

from ted_sws.core.model import PropertyBaseModel
from ted_sws.core.model.manifestation import Manifestation, ValidationSummaryReport
from ted_sws.core.model.notice import NoticeStatus


class SupraNotice(PropertyBaseModel, abc.ABC):
    """
        This is an arbitrary aggregate over a list of notices.
    """

    class Config:
        underscore_attrs_are_private = True
        validate_assignment = True
        orm_mode = True

    created_at: datetime = datetime.now().replace(microsecond=0)

    notice_ids: List[str]


class SupraNoticeValidationReport(Manifestation):
    """
        Result of checking whether all the notices published in TED are present in the internal database.
    """
    missing_notice_ids: Optional[List[str]] = None
    not_published_notice_ids: Optional[List[str]] = None

    def is_valid(self):
        if not self.missing_notice_ids and not self.not_published_notice_ids:
            return True
        return False


class DailySupraNotice(SupraNotice):
    """
        This is an aggregate over the notices published in TED in a specific day.
    """
    ted_publication_date: date
    validation_report: Optional[SupraNoticeValidationReport] = None
    validation_summary: Optional[ValidationSummaryReport] = None


class DailyNoticesMetadataABC(PropertyBaseModel):
    class Config:
        underscore_attrs_are_private = True
        validate_assignment = True
        orm_mode = True


NOTICE_STATUSES_DEFAULT_STATS = {str(notice_status): 0 for notice_status in NoticeStatus}


class DailyNoticesMetadata(DailyNoticesMetadataABC):
    """
        This is an aggregate over the notices published in TED in a specific day.
    """
    ted_api_notice_ids: List[str] = []
    fetched_notice_ids: List[str] = []
    aggregation_date: date

    mapping_suite_packages: List[str] = []  # unique list of used mapping_suite_packages

    notice_statuses: dict = NOTICE_STATUSES_DEFAULT_STATS

    @computed_field
    @property
    def notice_statuses_coverage(self) -> dict:
        ted_api_notice_count = self.ted_api_notice_count or 1
        return {f"{notice_status}_coverage": notice_status_count / ted_api_notice_count
                for notice_status, notice_status_count in self.notice_statuses.items()}

    @computed_field
    @property
    def ted_api_notice_count(self) -> int:
        return len(self.ted_api_notice_ids)

    @computed_field
    @property
    def fetched_notices_count(self) -> int:
        return len(self.fetched_notice_ids)
