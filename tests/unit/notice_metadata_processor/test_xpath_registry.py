from ted_sws.notice_metadata_processor.services.xpath_registry import XpathRegistry


def test_xpath_registry():
    xpath_registry = XpathRegistry()
    assert isinstance(xpath_registry.xpath_regulation, str)
    assert xpath_registry.xpath_ojs_type == "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:REF_OJS/manifestation_ns:COLL_OJ"
    assert xpath_registry.xpath_name_of_buyer_elements == "manifestation_ns:TRANSLATION_SECTION/manifestation_ns:ML_AA_NAMES/"
