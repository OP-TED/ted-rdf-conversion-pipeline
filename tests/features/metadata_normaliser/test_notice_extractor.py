from pytest_bdd import scenario, given, when, then

from ted_sws.metadata_normaliser.model.metadata import ExtractedMetadata
from ted_sws.metadata_normaliser.services.xml_manifestation_metadata_extractor import XMLManifestationMetadataExtractor
from ted_sws.notice_fetcher.adapters.ted_api import TedRequestAPI, TedAPIAdapter
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher


@scenario('notice_extractor.feature', 'Extracting metadata')
def test_extract_metadata():
    """Extracting metadata"""


@given("a notice", target_fixture="a_notice")
def step_impl(notice_identifier, api_end_point, fake_notice_storage):
    NoticeFetcher(notice_repository=fake_notice_storage,
                  ted_api_adapter=TedAPIAdapter(request_api=TedRequestAPI(), ted_api_url=api_end_point)).fetch_notice_by_id(
        document_id=notice_identifier)
    return fake_notice_storage.get(reference=notice_identifier)


@when("the extracting process is executed", target_fixture="extracting_process")
def step_impl(a_notice):
    return XMLManifestationMetadataExtractor(xml_manifestation=a_notice.xml_manifestation).to_metadata()



@then("a extracted metadata is available")
def step_impl(extracting_process,notice_identifier):
    assert isinstance(extracting_process, ExtractedMetadata)
    assert extracting_process.dict().keys() == ExtractedMetadata.__fields__.keys()
    assert notice_identifier in extracting_process.dict()["notice_publication_number"]
