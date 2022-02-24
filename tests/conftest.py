import base64
import json

import pytest

from ted_sws.domain.model.manifestation import XMLManifestation
from ted_sws.domain.model.metadata import TEDMetadata
from ted_sws.domain.model.notice import Notice
from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher
from tests import TEST_DATA_PATH
from tests.fakes.fake_ted_api import FakeRequestAPI
from tests.fakes.fake_repository import FakeNoticeRepository


@pytest.fixture
def notice_repository():
    return FakeNoticeRepository()

@pytest.fixture
def ted_document_search():
    return TedAPIAdapter(request_api=FakeRequestAPI())


@pytest.fixture
def raw_notice(ted_document_search) -> Notice:
    document_id = "067623-2022"
    return NoticeFetcher(ted_api_adapter=ted_document_search).get_notice_by_id(
        document_id=document_id)


def read_notice(notice_file: str):
    path = TEST_DATA_PATH / "notices" / notice_file
    return json.loads(path.read_text())


@pytest.fixture
def notice_2016():
    notice_data = read_notice("034224-2016.json")
    notice_content = base64.b64decode(notice_data["content"]).decode(encoding="utf-8")

    xml_manifestation = XMLManifestation(object_data=notice_content)

    del notice_data["content"]
    ted_id = notice_data["ND"]
    original_metadata = TEDMetadata(**notice_data)

    return Notice(ted_id=ted_id, xml_manifestation=xml_manifestation, original_metadata=original_metadata)


@pytest.fixture
def notice_2015():
    notice_data = read_notice("037067-2015.json")
    notice_content = base64.b64decode(notice_data["content"]).decode(encoding="utf-8")

    xml_manifestation = XMLManifestation(object_data=notice_content)

    del notice_data["content"]
    ted_id = notice_data["ND"]
    original_metadata = TEDMetadata(**notice_data)

    return Notice(ted_id=ted_id, xml_manifestation=xml_manifestation, original_metadata=original_metadata)


@pytest.fixture
def notice_2018():
    notice_data = read_notice("045279-2018.json")
    notice_content = base64.b64decode(notice_data["content"]).decode(encoding="utf-8")

    xml_manifestation = XMLManifestation(object_data=notice_content)

    del notice_data["content"]
    ted_id = notice_data["ND"]
    original_metadata = TEDMetadata(**notice_data)

    return Notice(ted_id=ted_id, xml_manifestation=xml_manifestation, original_metadata=original_metadata)
