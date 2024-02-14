import xml.etree.ElementTree as ET

from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.notice_metadata_processor.adapters.notice_metadata_extractor import EformsNoticeMetadataExtractor, \
    DefaultNoticeMetadataExtractor, extract_text_from_element, extract_attribute_from_element, \
    extract_code_and_value_from_element, parse_xml_manifestation, normalised_namespaces_from_xml_manifestation
from ted_sws.notice_metadata_processor.model.metadata import ExtractedMetadata, EncodedValue


def test_metadata_extractor(indexed_notice):
    metadata_extractor = DefaultNoticeMetadataExtractor(
        xml_manifestation=indexed_notice.xml_manifestation).extract_metadata()
    extracted_metadata_dict = metadata_extractor.dict()

    assert isinstance(metadata_extractor, ExtractedMetadata)
    assert extracted_metadata_dict.keys() == ExtractedMetadata.__fields__.keys()
    assert "extracted_form_number", "xml_schema" in extracted_metadata_dict.keys()
    assert "067623-2022" in extracted_metadata_dict["notice_publication_number"]
    assert "http://publications.europa.eu/resource/schema/ted/R2.0.8/publication TED_EXPORT.xsd" in \
           extracted_metadata_dict["xml_schema"]
    assert extracted_metadata_dict["extracted_form_number"] == "18"


def test_metadata_extractor_2016(notice_2016):
    metadata_extractor = DefaultNoticeMetadataExtractor(
        xml_manifestation=notice_2016.xml_manifestation).extract_metadata()

    extracted_metadata_dict = metadata_extractor.dict()
    assert isinstance(metadata_extractor, ExtractedMetadata)
    assert extracted_metadata_dict.keys() == ExtractedMetadata.__fields__.keys()
    assert notice_2016.ted_id in extracted_metadata_dict["notice_publication_number"]


def test_metadata_extractor_2015(notice_2015):
    metadata_extractor = DefaultNoticeMetadataExtractor(
        xml_manifestation=notice_2015.xml_manifestation).extract_metadata()

    extracted_metadata_dict = metadata_extractor.dict()
    assert isinstance(metadata_extractor, ExtractedMetadata)
    assert extracted_metadata_dict.keys() == ExtractedMetadata.__fields__.keys()
    assert notice_2015.ted_id in extracted_metadata_dict["notice_publication_number"]


def test_metadata_extractor_2018(notice_2018):
    metadata_extractor = DefaultNoticeMetadataExtractor(
        xml_manifestation=notice_2018.xml_manifestation).extract_metadata()

    extracted_metadata_dict = metadata_extractor.dict()
    assert isinstance(metadata_extractor, ExtractedMetadata)
    assert extracted_metadata_dict.keys() == ExtractedMetadata.__fields__.keys()
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
    manifestation_root = parse_xml_manifestation(xml_manifestation=indexed_notice.xml_manifestation)

    assert isinstance(manifestation_root, ET.Element)


def test_get_normalised_namespaces(indexed_notice):
    namespaces = normalised_namespaces_from_xml_manifestation(xml_manifestation=indexed_notice.xml_manifestation)

    assert isinstance(namespaces, dict)
    assert "manifestation_ns", "nuts" in namespaces.keys()


def test_metadata_eform_extractor(eform_notice_622690):
    metadata_extractor = EformsNoticeMetadataExtractor(
        xml_manifestation=eform_notice_622690.xml_manifestation).extract_metadata()
    extracted_metadata_dict = metadata_extractor.dict()
    assert isinstance(metadata_extractor, ExtractedMetadata)
    assert extracted_metadata_dict.keys() == ExtractedMetadata.__fields__.keys()
    assert "extracted_form_number", "xml_schema" in extracted_metadata_dict.keys()
    assert "00622690-2023" in extracted_metadata_dict["notice_publication_number"]
    assert "competition" in extracted_metadata_dict["extracted_eform_type"]
    assert extracted_metadata_dict["extracted_form_number"] == None


def _test_metadata_extractor_for_all_eforms_variations(eforms_xml_notice_paths):
    for xml_notice_path in eforms_xml_notice_paths:
        notice_id = xml_notice_path.name
        eforms_subtype = xml_notice_path.parent.name
        eforms_sdk_version = xml_notice_path.parent.parent.name
        try:
            notice_content = xml_notice_path.read_text(encoding="utf-8")
            extracted_metadata = EformsNoticeMetadataExtractor(
                xml_manifestation=XMLManifestation(object_data=notice_content)
            ).extract_metadata()
            extracted_metadata_dict = extracted_metadata.dict()
            assert isinstance(extracted_metadata, ExtractedMetadata)
            assert extracted_metadata_dict.keys() == ExtractedMetadata.__fields__.keys()
            assert "extracted_form_number", "xml_schema" in extracted_metadata_dict.keys()
        except Exception as e:
            raise Exception(f"Exception for {eforms_sdk_version}, {eforms_subtype}, notice_id:{notice_id}, exception:", str(e))

