import base64
import datetime
import json

import pytest

from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.core.model.metadata import TEDMetadata, LanguageTaggedString, NormalisedMetadata
from ted_sws.core.model.notice import Notice
from ted_sws.metadata_normaliser.services.metadata_normalizer import TITLE_KEY, LONG_TITLE_KEY, NOTICE_TYPE_KEY, \
    NOTICE_NUMBER_KEY, OJS_TYPE_KEY, OJS_NUMBER_KEY, LANGUAGE_KEY, EU_INSTITUTION_KEY, SENT_DATE_KEY, DEADLINE_DATE_KEY, \
    BUYER_COUNTRY_KEY, BUYER_NAME_KEY, BUYER_CITY_KEY, PUBLICATION_DATE_KEY, FORM_NUMBER_KEY, \
    FORM_TYPE_KEY, LEGAL_BASIS_DIRECTIVE_KEY, EXTRACTED_LEGAL_BASIS_KEY, \
    PLACE_OF_PERFORMANCE_KEY, E_FORMS_SUBTYPE_KEY, XSD_VERSION_KEY
from ted_sws.notice_fetcher.adapters.ted_api import TedAPIAdapter
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher
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
        TITLE_KEY: [
            LanguageTaggedString(text='Услуги по ремонт и поддържане на превозни средства с военна употреба',
                                 language='BG'),
            LanguageTaggedString(text='Repair and maintenance services of military vehicles', language='GA')
        ],
        LONG_TITLE_KEY: [
            LanguageTaggedString(
                text='Гepмaния :: Бон :: Услуги по ремонт и поддържане на превозни средства с военна употреба',
                language='BG'),
            LanguageTaggedString(text='Tyskland :: Bonn :: Reparation och underhåll av militärfordon',
                                 language='SV')
        ],
        NOTICE_NUMBER_KEY: '067623-2022',
        PUBLICATION_DATE_KEY: datetime.date(2022, 2, 7).isoformat(),
        OJS_NUMBER_KEY: '26',
        OJS_TYPE_KEY: 'S',
        BUYER_CITY_KEY: [
            LanguageTaggedString(text='Бон', language='BG'),
            LanguageTaggedString(text='Bonn', language='SV')
        ],
        BUYER_NAME_KEY: [
            LanguageTaggedString(text='HIL Heeresinstandsetzungslogistik GmbH', language='DE')
        ],
        LANGUAGE_KEY: 'http://publications.europa.eu/resource/authority/language/DEU',
        BUYER_COUNTRY_KEY: 'http://publications.europa.eu/resource/authority/country/DEU',
        EU_INSTITUTION_KEY: False,
        SENT_DATE_KEY: datetime.date(2022, 2, 2).isoformat(),
        DEADLINE_DATE_KEY: None,
        NOTICE_TYPE_KEY: 'AWESOME_NOTICE_TYPE',
        FORM_TYPE_KEY: '18',
        PLACE_OF_PERFORMANCE_KEY: ['http://data.europa.eu/nuts/code/DE'],
        EXTRACTED_LEGAL_BASIS_KEY: 'http://publications.europa.eu/resource/authority/legal-basis/32009L0081',
        FORM_NUMBER_KEY: 'F18',
        LEGAL_BASIS_DIRECTIVE_KEY: 'http://publications.europa.eu/resource/authority/legal-basis/32009L0081',
        E_FORMS_SUBTYPE_KEY: 16,
        XSD_VERSION_KEY: "R2.0.9.S04.E01"
    }

    return data


@pytest.fixture
def normalised_metadata_object():
    data = {
        TITLE_KEY: [
            LanguageTaggedString(text='Услуги по ремонт и поддържане на превозни средства с военна употреба',
                                 language='BG'),
            LanguageTaggedString(text='Repair and maintenance services of military vehicles', language='GA')
        ],
        LONG_TITLE_KEY: [
            LanguageTaggedString(
                text='Гepмaния :: Бон :: Услуги по ремонт и поддържане на превозни средства с военна употреба',
                language='BG'),
            LanguageTaggedString(text='Tyskland :: Bonn :: Reparation och underhåll av militärfordon',
                                 language='SV')
        ],
        NOTICE_NUMBER_KEY: '067623-2022',
        PUBLICATION_DATE_KEY: datetime.date(2020, 3, 8).isoformat(),
        OJS_NUMBER_KEY: '26',
        OJS_TYPE_KEY: 'S',
        BUYER_CITY_KEY: [
            LanguageTaggedString(text='Бон', language='BG'),
            LanguageTaggedString(text='Bonn', language='SV')
        ],
        BUYER_NAME_KEY: [
            LanguageTaggedString(text='HIL Heeresinstandsetzungslogistik GmbH', language='DE')
        ],
        LANGUAGE_KEY: 'http://publications.europa.eu/resource/authority/language/DEU',
        BUYER_COUNTRY_KEY: 'http://publications.europa.eu/resource/authority/country/DEU',
        EU_INSTITUTION_KEY: False,
        SENT_DATE_KEY: datetime.date(2022, 2, 2).isoformat(),
        DEADLINE_DATE_KEY: None,
        NOTICE_TYPE_KEY: 'AWESOME_NOTICE_TYPE',
        FORM_TYPE_KEY: 'http://publications.europa.eu/resource/authority/form-type/planning',
        PLACE_OF_PERFORMANCE_KEY: ['http://data.europa.eu/nuts/code/DE'],
        EXTRACTED_LEGAL_BASIS_KEY: 'http://publications.europa.eu/resource/authority/legal-basis/32014L0024',
        FORM_NUMBER_KEY: 'F03',
        LEGAL_BASIS_DIRECTIVE_KEY: 'http://publications.europa.eu/resource/authority/legal-basis/32014L0024',
        E_FORMS_SUBTYPE_KEY: 12,
        XSD_VERSION_KEY: "R2.0.9.S04.E01"
    }

    return NormalisedMetadata(**data)
