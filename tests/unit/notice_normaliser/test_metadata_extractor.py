from ted_sws.domain.model.metadata import ExtractedMetadata
from ted_sws.metadata_normaliser.services.xml_manifestation_metadata_extractor import extract_text_from_elements, \
    extract_attribute_value_from_elements

import xml.etree.ElementTree as ET

from ted_sws.metadata_normaliser.services.extract_metadata import MetadataExtractor


def test_metadata_extractor(raw_notice):
    metadata_extractor = MetadataExtractor(notice=raw_notice).extract_metadata()

    extracted_metadata_dict = metadata_extractor.dict()

    assert isinstance(metadata_extractor, ExtractedMetadata)
    assert extracted_metadata_dict.keys() == ExtractedMetadata.__fields__.keys()
    assert "067623-2022" in extracted_metadata_dict["notice_publication_number"]


def test_metadata_extractor_2016(notice_2016):
    metadata_extractor = MetadataExtractor(notice=notice_2016).extract_metadata()

    extracted_metadata_dict = metadata_extractor.dict()
    assert isinstance(metadata_extractor, ExtractedMetadata)
    assert extracted_metadata_dict.keys() == ExtractedMetadata.__fields__.keys()
    assert notice_2016.ted_id in extracted_metadata_dict["notice_publication_number"]


def test_metadata_extractor_2015(notice_2015):
    metadata_extractor = MetadataExtractor(notice=notice_2015).extract_metadata()

    extracted_metadata_dict = metadata_extractor.dict()
    assert isinstance(metadata_extractor, ExtractedMetadata)
    assert extracted_metadata_dict.keys() == ExtractedMetadata.__fields__.keys()
    assert notice_2015.ted_id in extracted_metadata_dict["notice_publication_number"]

def test_metadata_extractor_2018(notice_2018):
    metadata_extractor = MetadataExtractor(notice=notice_2018).extract_metadata()

    extracted_metadata_dict = metadata_extractor.dict()
    assert isinstance(metadata_extractor, ExtractedMetadata)
    assert extracted_metadata_dict.keys() == ExtractedMetadata.__fields__.keys()
    assert notice_2018.ted_id in extracted_metadata_dict["notice_publication_number"]



def test_xpath_extract_data(raw_notice):
    doc_root = ET.fromstring(raw_notice.xml_manifestation.object_data)
    namespace = {"epo": "http://publications.europa.eu/resource/schema/ted/R2.0.8/publication"}

    list_of_elements = doc_root.findall("epo:TRANSLATION_SECTION/epo:ML_TITLES/epo:ML_TI_DOC[@LG='EN']/",
                                        namespaces=namespace)

    extracted_data = extract_text_from_elements(elements=list_of_elements)

    assert isinstance(extracted_data, list)
    assert "Germany" in extracted_data


def test_xpath_extract_attributes(raw_notice):
    doc_root = ET.fromstring(raw_notice.xml_manifestation.object_data)
    namespace = {"epo": "http://publications.europa.eu/resource/schema/ted/R2.0.8/publication"}
    list_of_elements = doc_root.findall("epo:CODED_DATA_SECTION/epo:NOTICE_DATA/epo:ISO_COUNTRY", namespaces=namespace)

    extracted_data = extract_attribute_value_from_elements(elements=list_of_elements, attrib_key="VALUE")

    assert isinstance(extracted_data, list)
    assert "DE" in extracted_data
