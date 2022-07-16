#!/usr/bin/python3

# supra_notice.py
# Date:  16/07/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" This module implements aggregates over groups of notices and the appropriate business needs, on those groups """
import abc
import json
from datetime import datetime, date
from typing import List

from ted_sws.core.model import PropertyBaseModel
from ted_sws.core.model.manifestation import Manifestation


class SupraNotice(PropertyBaseModel, abc.ABC):
    """
        This is an arbitrary aggregate over a list of notices.
    """

    class Config:
        underscore_attrs_are_private = True
        validate_assignment = True
        orm_mode = True

    created_at: datetime = datetime.now()

    notice_ids: List[str]


class SupraNoticeValidationReport(Manifestation):
    """
        Result of checking whether all the notices published in TED are present in the internal database.
    """
    missing_notice_ids: List[str]

    def is_valid(self):
        if not self.missing_notice_ids:
            return True
        return False


class DailySupraNotice(SupraNotice):
    """
        This is an aggregate over the notices published in TED in a specific day.
    """
    notice_publication_day: date = datetime.today()
    validation_report: SupraNoticeValidationReport = None
