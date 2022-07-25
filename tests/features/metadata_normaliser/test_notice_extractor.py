from pytest_bdd import scenario, given, when, then, parsers

from ted_sws.notice_metadata_processor.model.metadata import ExtractedMetadata
from ted_sws.notice_metadata_processor.services.xml_manifestation_metadata_extractor import XMLManifestationMetadataExtractor
from ted_sws.notice_fetcher.adapters.ted_api import TedRequestAPI, TedAPIAdapter
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher


@scenario('notice_extractor.feature', 'Extracting metadata')
def test_extract_metadata():
    """Extracting metadata"""


@given("an XML manifestation", target_fixture="xml_manifestation")
def step_impl(notice_identifier, api_end_point, fake_notice_storage):
    NoticeFetcher(notice_repository=fake_notice_storage,
                  ted_api_adapter=TedAPIAdapter(request_api=TedRequestAPI(),
                                                ted_api_url=api_end_point)).fetch_notice_by_id(
        document_id=notice_identifier)
    return fake_notice_storage.get(reference=notice_identifier).xml_manifestation


@when("the extracting process is executed", target_fixture="extracted_metadata")
def step_impl(xml_manifestation):
    return XMLManifestationMetadataExtractor(xml_manifestation=xml_manifestation).to_metadata()


@then(parsers.parse("extracted {metadata} is possibly available"))
def step_impl(extracted_metadata, notice_identifier, metadata):
    assert isinstance(extracted_metadata, ExtractedMetadata)
    assert extracted_metadata.dict().keys() == ExtractedMetadata.__fields__.keys()
    assert notice_identifier == extracted_metadata.dict()["notice_publication_number"]
    assert metadata in extracted_metadata.dict()
