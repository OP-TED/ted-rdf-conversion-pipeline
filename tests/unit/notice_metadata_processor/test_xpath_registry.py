from ted_sws.notice_metadata_processor.adapters.xpath_registry import DefaultXPathRegistry, EformsXPathRegistry


def test_default_xpath_registry():
    xpath_registry = DefaultXPathRegistry()
    assert isinstance(xpath_registry.xpath_regulation, str)
    assert xpath_registry.xpath_ojs_type == "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:REF_OJS/manifestation_ns:COLL_OJ"
    assert xpath_registry.xpath_name_of_buyer_elements == "manifestation_ns:TRANSLATION_SECTION/manifestation_ns:ML_AA_NAMES/"


def test_eforms_xpath_registry():
    xpath_registry = EformsXPathRegistry()
    assert isinstance(xpath_registry.xpath_notice_type, str)
    assert xpath_registry.xpath_notice_subtype == ".//ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeSubType/cbc:SubTypeCode[@listName='notice-subtype']"
    assert xpath_registry.xpath_notice_type == ".//cbc:NoticeTypeCode"