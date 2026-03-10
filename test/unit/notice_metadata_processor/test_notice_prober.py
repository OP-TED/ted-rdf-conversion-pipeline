from src.ted_sws.notice_metadata_processor.services.notice_prober import NoticeProber
from test.unit.notice_metadata_processor import load_mapping_suite_and_package


def test_notice_prober(eform_notice_622690, mongodb_client, load_mapping_suite_and_package):
    notice_prober = NoticeProber(xml_manifestation=eform_notice_622690.xml_manifestation, mongodb_client=mongodb_client)
    mapping_suite = notice_prober.get_mapping_suite()
    assert mapping_suite
