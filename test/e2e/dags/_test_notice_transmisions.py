#!/usr/bin/python3
import pickle

from deepdiff import DeepDiff
from src.ted_sws.data_manager.adapters.notice_repository import NoticeRepository


def test_notice_is_convertible_to_dict(notice_2021):
    notice = notice_2021
    notice_dict = NoticeRepository._create_dict_from_notice(notice)
    result_notice = NoticeRepository._create_notice_from_repository_result(notice_dict)
    assert DeepDiff(notice.model_dump(), result_notice.model_dump(), ignore_order=True) == {}


def test_notice_is_convertible_to_pickle(notice_2021):
    notice = notice_2021
    notice_dump = pickle.dumps(notice)
    result_notice = pickle.loads(notice_dump)
    assert DeepDiff(notice.model_dump(), result_notice.model_dump(), ignore_order=True) == {}
