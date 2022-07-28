import json
import pathlib
import shutil
import tempfile

import deepdiff
from deepdiff import DeepDiff
from pymongo import MongoClient

from ted_sws import config
from ted_sws.core.model.manifestation import RDFManifestation
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository, NoticeRepositoryInFileSystem
from ted_sws.mapping_suite_processor.services.conceptual_mapping_processor import \
    mapping_suite_processor_from_github_expand_and_load_package_in_mongo_db
from tests import TEST_DATA_PATH

NOTICE_REPOSITORY_NAME = "notice_repository"
NOTICE_REPOSITORY_PATH = TEST_DATA_PATH / NOTICE_REPOSITORY_NAME
MAPPING_SUITE_PACKAGE_NAME = "package_F03_test"


def test_notice_repository_in_file_system(notice_2018, notice_2020, notice_2021):
    notices = [notice_2018, notice_2020, notice_2021]
    with tempfile.TemporaryDirectory() as tmp_dirname:
        notice_repository_fs = NoticeRepositoryInFileSystem(repository_path=tmp_dirname)
        for notice in notices:
            notice._rdf_manifestation = RDFManifestation(object_data="test_data")
            notice_repository_fs.add(notice)
        assert len(list(notice_repository_fs.list())) == 3
        for notice in notices:
            notice_repository_fs.update(notice)
        assert len(list(notice_repository_fs.list())) == 3
        for notice in notices:
            my_notice = notice_repository_fs.get(notice.ted_id)
            assert my_notice.ted_id == notice.ted_id
            assert my_notice.xml_manifestation.object_data == notice.xml_manifestation.object_data
            assert my_notice.rdf_manifestation.object_data == notice.rdf_manifestation.object_data
