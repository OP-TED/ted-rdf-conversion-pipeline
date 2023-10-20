import xml.etree.ElementTree as ET

from ted_sws.notice_metadata_processor.adapters.notice_metadata_extractor_prototype import EformsNoticeMetadataExtractor
from ted_sws.notice_metadata_processor.adapters.xpath_registry import EformsXPathRegistry
from ted_sws.notice_metadata_processor.model.metadata import ExtractedMetadata, EncodedValue
from ted_sws.notice_metadata_processor.services.metadata_normalizer import check_if_xml_manifestation_is_eform
from ted_sws.notice_metadata_processor.services.xml_manifestation_metadata_extractor import extract_text_from_element, \
    extract_attribute_from_element, XMLManifestationMetadataExtractor, extract_code_and_value_from_element


def test_metadata_extractor(indexed_notice):
    metadata_extractor = XMLManifestationMetadataExtractor(
        xml_manifestation=indexed_notice.xml_manifestation).to_metadata()
    extracted_metadata_dict = metadata_extractor.model_dump()

    assert isinstance(metadata_extractor, ExtractedMetadata)
    assert extracted_metadata_dict.keys() == ExtractedMetadata.model_fields.keys()
    assert "extracted_form_number", "xml_schema" in extracted_metadata_dict.keys()
    assert "067623-2022" in extracted_metadata_dict["notice_publication_number"]
    assert "http://publications.europa.eu/resource/schema/ted/R2.0.8/publication TED_EXPORT.xsd" in \
           extracted_metadata_dict["xml_schema"]
    assert extracted_metadata_dict["extracted_form_number"] == "18"


def test_metadata_extractor_2016(notice_2016):
    metadata_extractor = XMLManifestationMetadataExtractor(
        xml_manifestation=notice_2016.xml_manifestation).to_metadata()

    extracted_metadata_dict = metadata_extractor.model_dump()
    assert isinstance(metadata_extractor, ExtractedMetadata)
    assert extracted_metadata_dict.keys() == ExtractedMetadata.model_fields.keys()
    assert notice_2016.ted_id in extracted_metadata_dict["notice_publication_number"]


def test_metadata_extractor_2015(notice_2015):
    metadata_extractor = XMLManifestationMetadataExtractor(
        xml_manifestation=notice_2015.xml_manifestation).to_metadata()

    extracted_metadata_dict = metadata_extractor.model_dump()
    assert isinstance(metadata_extractor, ExtractedMetadata)
    assert extracted_metadata_dict.keys() == ExtractedMetadata.model_fields.keys()
    assert notice_2015.ted_id in extracted_metadata_dict["notice_publication_number"]


def test_metadata_extractor_2018(notice_2018):
    metadata_extractor = XMLManifestationMetadataExtractor(
        xml_manifestation=notice_2018.xml_manifestation).to_metadata()

    extracted_metadata_dict = metadata_extractor.model_dump()
    assert isinstance(metadata_extractor, ExtractedMetadata)
    assert extracted_metadata_dict.keys() == ExtractedMetadata.model_fields.keys()
    assert notice_2018.ted_id in extracted_metadata_dict["notice_publication_number"]


def test_xpath_extract_data(indexed_notice):
    doc_root = ET.fromstring(indexed_notice.xml_manifestation.object_data)
    namespace = {"epo": "http://publications.europa.eu/resource/schema/ted/R2.0.8/publication"}

    list_of_elements = doc_root.findall("epo:TRANSLATION_SECTION/epo:ML_TITLES/epo:ML_TI_DOC[@LG='EN']/",
                                        namespaces=namespace)

    extracted_data = extract_text_from_element(element=list_of_elements[0])

    assert isinstance(extracted_data, str)
    assert "Germany" in extracted_data


def test_xpath_extract_attribute(indexed_notice):
    doc_root = ET.fromstring(indexed_notice.xml_manifestation.object_data)
    namespace = {"epo": "http://publications.europa.eu/resource/schema/ted/R2.0.8/publication"}
    element = doc_root.find("epo:CODED_DATA_SECTION/epo:NOTICE_DATA/epo:ISO_COUNTRY", namespaces=namespace)

    extracted_data = extract_attribute_from_element(element=element, attrib_key="VALUE")

    assert isinstance(extracted_data, str)
    assert "DE" in extracted_data


def test_extract_code_and_value(indexed_notice):
    doc_root = ET.fromstring(indexed_notice.xml_manifestation.object_data)
    namespace = {"epo": "http://publications.europa.eu/resource/schema/ted/R2.0.8/publication"}
    element = doc_root.find("epo:CODED_DATA_SECTION/epo:CODIF_DATA/epo:NC_CONTRACT_NATURE", namespaces=namespace)

    extracted_data = extract_code_and_value_from_element(element=element)
    assert isinstance(extracted_data, EncodedValue)
    assert extracted_data.value == "Services"
    assert extracted_data.code == "4"

    nonexisting_element = doc_root.find("epo:CODED_DATA_SECTION/epo:CODIF_DATA/NC_CONTRACT_NATURE",
                                        namespaces=namespace)
    extracted_data = extract_code_and_value_from_element(element=nonexisting_element)

    assert extracted_data is None


def test_get_root_of_manifestation(indexed_notice):
    manifestation_root = XMLManifestationMetadataExtractor(
        xml_manifestation=indexed_notice.xml_manifestation)._parse_manifestation()

    assert isinstance(manifestation_root, ET.Element)


def test_get_normalised_namespaces(indexed_notice):
    namespaces = XMLManifestationMetadataExtractor(
        xml_manifestation=indexed_notice.xml_manifestation)._get_normalised_namespaces()

    assert isinstance(namespaces, dict)
    assert "manifestation_ns", "nuts" in namespaces.keys()


def test_check_if_xml_manifestation_is_eform(eform_notice_622690, notice_2018):
    is_eform_notice_622690_a_eform = check_if_xml_manifestation_is_eform(
        xml_manifestation=eform_notice_622690.xml_manifestation)
    is_notice_2018_a_eform = check_if_xml_manifestation_is_eform(xml_manifestation=notice_2018.xml_manifestation)

    assert is_eform_notice_622690_a_eform == True
    assert is_notice_2018_a_eform == False



def test_eform_xpath(eform_notice_622690):
    namespaces = XMLManifestationMetadataExtractor(
        xml_manifestation=eform_notice_622690.xml_manifestation)._get_normalised_namespaces()
    # print(namespaces)
    doc_root = ET.fromstring(eform_notice_622690.xml_manifestation.object_data)
    xpaths = EformsXPathRegistry()
    # element = doc_root.find(".//ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeSubType/cbc:SubTypeCode", namespaces=namespaces).text
    # element = doc_root.find(".//ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:Publication/efbc:PublicationDate", namespaces=namespaces).text
    # element = doc_root.find(".//cbc:RegulatoryDomain", namespaces=namespaces).text
    # element = doc_root.find(".//cbc:RegulatoryDomain", namespaces=namespaces).text
    # element = doc_root.find(".//cac:ProcurementProject/cac:MainCommodityClassification/cbc:ItemClassificationCode[@listName='cpv']", namespaces=namespaces).text
    xpath_title = doc_root.find(xpaths.xpath_title, namespaces=namespaces).text
    xpath_title_country = doc_root.find(xpaths.xpath_title_country, namespaces=namespaces).text
    xpath_publication_date = doc_root.find(xpaths.xpath_publication_date, namespaces=namespaces).text
    xpath_ojs_issue_number = doc_root.find(xpaths.xpath_ojs_issue_number, namespaces=namespaces).text
    xpath_original_language = doc_root.find(xpaths.xpath_original_language, namespaces=namespaces).text
    xpath_document_sent_date = doc_root.find(xpaths.xpath_document_sent_date, namespaces=namespaces).text
    xpath_type_of_contract = doc_root.find(xpaths.xpath_type_of_contract, namespaces=namespaces).text
    xpath_type_of_procedure = doc_root.find(xpaths.xpath_type_of_procedure, namespaces=namespaces).text
    xpath_place_of_performance = doc_root.find(xpaths.xpath_place_of_performance, namespaces=namespaces).text
    xpath_internet_address = doc_root.find(xpaths.xpath_internet_address, namespaces=namespaces).text
    xpath_legal_basis_directive = doc_root.find(xpaths.xpath_legal_basis_directive, namespaces=namespaces).text
    xpath_notice_subtype = doc_root.find(xpaths.xpath_notice_subtype, namespaces=namespaces).text
    xpath_form_type = doc_root.find(xpaths.xpath_form_type, namespaces=namespaces).attrib["listName"]
    xpath_notice_type = doc_root.find(xpaths.xpath_notice_type, namespaces=namespaces).text
    print(xpath_title)
    print(xpath_title_country)
    print(xpath_publication_date)
    print(xpath_ojs_issue_number)
    print(xpath_original_language)
    print(xpath_document_sent_date)
    print(xpath_type_of_contract)
    print(xpath_type_of_procedure)
    print(xpath_place_of_performance)
    print(xpath_internet_address)
    print(xpath_legal_basis_directive)
    print(xpath_notice_subtype)
    print(xpath_form_type)
    print(xpath_notice_type)


def test_metadata_eform_extractor(eform_notice_622690):
    metadata_extractor = EformsNoticeMetadataExtractor(
        xml_manifestation=eform_notice_622690.xml_manifestation).extract_metadata()
    extracted_metadata_dict = metadata_extractor.model_dump()
    print(extracted_metadata_dict)
    assert isinstance(metadata_extractor, ExtractedMetadata)
    assert extracted_metadata_dict.keys() == ExtractedMetadata.model_fields.keys()
    assert "extracted_form_number", "xml_schema" in extracted_metadata_dict.keys()
    assert "00622690-2023" in extracted_metadata_dict["notice_publication_number"]
    assert "competition" in extracted_metadata_dict["extracted_eform_type"]
    assert extracted_metadata_dict["extracted_form_number"] == None
