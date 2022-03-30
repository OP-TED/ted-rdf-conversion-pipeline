import base64
import datetime
import json

import pytest

from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.core.model.metadata import TEDMetadata, LanguageTaggedString, NormalisedMetadata
from ted_sws.core.model.notice import Notice
from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher
from ted_sws.notice_packager.model.metadata import NoticeMetadata
from tests import TEST_DATA_PATH
from tests.fakes.fake_repository import FakeNoticeRepository
from tests.fakes.fake_ted_api import FakeRequestAPI


@pytest.fixture
def notice_id():
    return "067623-2022"


@pytest.fixture
def notice_repository():
    return FakeNoticeRepository()


@pytest.fixture
def ted_document_search():
    return TedAPIAdapter(request_api=FakeRequestAPI())


@pytest.fixture
def raw_notice(ted_document_search, notice_repository, notice_id) -> Notice:
    document_id = notice_id
    NoticeFetcher(ted_api_adapter=ted_document_search, notice_repository=notice_repository).fetch_notice_by_id(
        document_id=document_id)
    raw_notice = notice_repository.get(reference=document_id)
    return raw_notice


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

@pytest.fixture
def notice_2020():
    notice_data = read_notice("408313-2020.json")
    notice_content = base64.b64decode(notice_data["content"]).decode(encoding="utf-8")
    xml_manifestation = XMLManifestation(object_data=notice_content)

    del notice_data["content"]
    ted_id = notice_data["ND"]
    original_metadata = TEDMetadata(**notice_data)

    return Notice(ted_id=ted_id, xml_manifestation=xml_manifestation, original_metadata=original_metadata)

@pytest.fixture
def normalised_metadata_dict():
    data = {
        'title': [
            LanguageTaggedString(text='Услуги по ремонт и поддържане на превозни средства с военна употреба',
                                 language='BG'),
            LanguageTaggedString(text='Repair and maintenance services of military vehicles', language='GA')
        ],
        'long_title': [
            LanguageTaggedString(
                text='Гepмaния :: Бон :: Услуги по ремонт и поддържане на превозни средства с военна употреба',
                language='BG'),
            LanguageTaggedString(text='Tyskland :: Bonn :: Reparation och underhåll av militärfordon',
                                 language='SV')
        ],
        'notice_publication_number': '067623-2022',
        'publication_date': datetime.date(2022, 2, 7),
        'ojs_issue_number': '26',
        'ojs_type': 'S',
        'city_of_buyer': [
            LanguageTaggedString(text='Бон', language='BG'),
            LanguageTaggedString(text='Bonn', language='SV')
        ],
        'name_of_buyer': [
            LanguageTaggedString(text='HIL Heeresinstandsetzungslogistik GmbH', language='DE')
        ],
        'original_language': 'http://publications.europa.eu/resource/authority/language/DEU',
        'country_of_buyer': 'http://publications.europa.eu/resource/authority/country/DEU',
        'eu_institution': False,
        'document_sent_date': datetime.date(2022, 2, 2),
        'deadline_for_submission': None,
        'notice_type': 'AWESOME_NOTICE_TYPE',
        'form_type': '18',
        'place_of_performance': ['http://data.europa.eu/nuts/code/DE'],
        'legal_basis_directive': 'http://publications.europa.eu/resource/authority/legal-basis/32009L0081',
        'form_number': 'F18'
    }

    return data


@pytest.fixture
def normalised_metadata_object():
    data = {
        'title': [
            LanguageTaggedString(text='Услуги по ремонт и поддържане на превозни средства с военна употреба',
                                 language='BG'),
            LanguageTaggedString(text='Repair and maintenance services of military vehicles', language='GA')
        ],
        'long_title': [
            LanguageTaggedString(
                text='Гepмaния :: Бон :: Услуги по ремонт и поддържане на превозни средства с военна употреба',
                language='BG'),
            LanguageTaggedString(text='Tyskland :: Bonn :: Reparation och underhåll av militärfordon',
                                 language='SV')
        ],
        'notice_publication_number': '067623-2022',
        'publication_date': datetime.date(2020, 2, 7),
        'ojs_issue_number': '26',
        'ojs_type': 'S',
        'city_of_buyer': [
            LanguageTaggedString(text='Бон', language='BG'),
            LanguageTaggedString(text='Bonn', language='SV')
        ],
        'name_of_buyer': [
            LanguageTaggedString(text='HIL Heeresinstandsetzungslogistik GmbH', language='DE')
        ],
        'original_language': 'http://publications.europa.eu/resource/authority/language/DEU',
        'country_of_buyer': 'http://publications.europa.eu/resource/authority/country/DEU',
        'eu_institution': False,
        'document_sent_date': datetime.date(2022, 2, 2),
        'deadline_for_submission': None,
        'notice_type': 'AWESOME_NOTICE_TYPE',
        'form_type': 'http://publications.europa.eu/resource/authority/form-type/planning',
        'place_of_performance': ['http://data.europa.eu/nuts/code/DE'],
        'legal_basis_directive': 'http://publications.europa.eu/resource/authority/legal-basis/32014L0024',
        'form_number': 'F03'
    }

    return NormalisedMetadata(**data)
