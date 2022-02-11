import base64
import json
import pathlib

import pytest

from ted_sws.notice_fetcher.adapters.ted_api import TedDocumentSearch
from tests.fakes.fake_ted_api import FakeRequestAPI



@pytest.fixture
def ted_document_search():
    return TedDocumentSearch(request_api=FakeRequestAPI())
