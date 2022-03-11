from ted_sws.metadata_normaliser.model.metadata import ExtractedMetadata, EncodedValue
from ted_sws.metadata_normaliser.services.xml_manifestation_metadata_extractor import extract_text_from_element, \
    extract_attribute_from_element, XMLManifestationMetadataExtractor, extract_code_and_value_from_element

import xml.etree.ElementTree as ET


def test_metadata_extractor(raw_notice):
    metadata_extractor = XMLManifestationMetadataExtractor(xml_manifestation=raw_notice.xml_manifestation).to_metadata()

    extracted_metadata_dict = metadata_extractor.dict()
    print (extracted_metadata_dict)

    assert isinstance(metadata_extractor, ExtractedMetadata)
    assert extracted_metadata_dict.keys() == ExtractedMetadata.__fields__.keys()
    assert "067623-2022" in extracted_metadata_dict["notice_publication_number"]


def test_metadata_extractor_2016(notice_2016):
    metadata_extractor = XMLManifestationMetadataExtractor(
        xml_manifestation=notice_2016.xml_manifestation).to_metadata()

    extracted_metadata_dict = metadata_extractor.dict()
    assert isinstance(metadata_extractor, ExtractedMetadata)
    assert extracted_metadata_dict.keys() == ExtractedMetadata.__fields__.keys()
    assert notice_2016.ted_id in extracted_metadata_dict["notice_publication_number"]


def test_metadata_extractor_2015(notice_2015):
    metadata_extractor = XMLManifestationMetadataExtractor(
        xml_manifestation=notice_2015.xml_manifestation).to_metadata()

    extracted_metadata_dict = metadata_extractor.dict()
    assert isinstance(metadata_extractor, ExtractedMetadata)
    assert extracted_metadata_dict.keys() == ExtractedMetadata.__fields__.keys()
    assert notice_2015.ted_id in extracted_metadata_dict["notice_publication_number"]


def test_metadata_extractor_2018(notice_2018):
    metadata_extractor = XMLManifestationMetadataExtractor(
        xml_manifestation=notice_2018.xml_manifestation).to_metadata()

    extracted_metadata_dict = metadata_extractor.dict()
    assert isinstance(metadata_extractor, ExtractedMetadata)
    assert extracted_metadata_dict.keys() == ExtractedMetadata.__fields__.keys()
    assert notice_2018.ted_id in extracted_metadata_dict["notice_publication_number"]


def test_xpath_extract_data(raw_notice):
    doc_root = ET.fromstring(raw_notice.xml_manifestation.object_data)
    namespace = {"epo": "http://publications.europa.eu/resource/schema/ted/R2.0.8/publication"}

    list_of_elements = doc_root.findall("epo:TRANSLATION_SECTION/epo:ML_TITLES/epo:ML_TI_DOC[@LG='EN']/",
                                        namespaces=namespace)

    extracted_data = extract_text_from_element(element=list_of_elements[0])

    assert isinstance(extracted_data, str)
    assert "Germany" in extracted_data


def test_xpath_extract_attribute(raw_notice):
    doc_root = ET.fromstring(raw_notice.xml_manifestation.object_data)
    namespace = {"epo": "http://publications.europa.eu/resource/schema/ted/R2.0.8/publication"}
    element = doc_root.find("epo:CODED_DATA_SECTION/epo:NOTICE_DATA/epo:ISO_COUNTRY", namespaces=namespace)

    extracted_data = extract_attribute_from_element(element=element, attrib_key="VALUE")

    assert isinstance(extracted_data, str)
    assert "DE" in extracted_data


def test_extract_code_and_value(raw_notice):
    doc_root = ET.fromstring(raw_notice.xml_manifestation.object_data)
    namespace = {"epo": "http://publications.europa.eu/resource/schema/ted/R2.0.8/publication"}
    element = doc_root.find("epo:CODED_DATA_SECTION/epo:CODIF_DATA/epo:NC_CONTRACT_NATURE", namespaces=namespace)

    extracted_data = extract_code_and_value_from_element(element=element)
    assert isinstance(extracted_data, EncodedValue)
    assert extracted_data.value == "Services"
    assert extracted_data.code == "4"

    nonexisting_element = doc_root.find("epo:CODED_DATA_SECTION/epo:CODIF_DATA/NC_CONTRACT_NATURE", namespaces=namespace)
    extracted_data = extract_code_and_value_from_element(element=nonexisting_element)

    assert extracted_data is None


def test_get_root_of_manifestation(raw_notice):
    manifestation_root = XMLManifestationMetadataExtractor(
        xml_manifestation=raw_notice.xml_manifestation)._parse_manifestation()

    assert isinstance(manifestation_root, ET.Element)


def test_get_normalised_namespaces(raw_notice):
    namespaces = XMLManifestationMetadataExtractor(
        xml_manifestation=raw_notice.xml_manifestation)._get_normalised_namespaces()

    assert isinstance(namespaces, dict)
    assert "manifestation_ns", "nuts" in namespaces.keys()
