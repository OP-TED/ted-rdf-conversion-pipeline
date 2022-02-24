from pytest_bdd import scenario, given, when, then

from ted_sws.domain.model.metadata import ExtractedMetadata
from ted_sws.metadata_normaliser.services.extract_metadata import MetadataExtractor
from ted_sws.notice_fetcher.adapters.ted_api import TedRequestAPI, TedAPIAdapter
from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher


@scenario('notice_extractor.feature', 'Extracting metadata')
def test_extract_metadata():
    """Fetch a TED notice"""

@given("a notice", target_fixture="a_notice")
def step_impl(notice_identifier, api_end_point):
    return NoticeFetcher(
        ted_api_adapter=TedAPIAdapter(request_api=TedRequestAPI(), ted_api_url=api_end_point)).get_notice_by_id(
        document_id=notice_identifier)


@when("the extracting process is executed", target_fixture="extracting_process")
def step_impl(a_notice):
    return MetadataExtractor(notice=a_notice).extract_metadata()



@then("a extracted metadata is available")
def step_impl(extracting_process,notice_identifier):
    assert isinstance(extracting_process, ExtractedMetadata)
    assert extracting_process.dict().keys() == ExtractedMetadata.__fields__.keys()
    assert notice_identifier in extracting_process.dict()["notice_publication_number"]
