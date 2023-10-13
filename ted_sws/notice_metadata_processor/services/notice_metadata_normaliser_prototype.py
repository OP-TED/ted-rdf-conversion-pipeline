from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.core.model.metadata import NormalisedMetadata
from ted_sws.core.model.notice import Notice
from ted_sws.notice_metadata_processor.adapters.notice_metada_normaliser_prototype import NoticeMetadataNormaliserABC, \
    EformsNoticeMetadataNormaliser, DefaultNoticeMetadataNormaliser
from ted_sws.notice_metadata_processor.adapters.notice_metadata_extractor_prototype import NoticeMetadataExtractorABC, \
    EformsNoticeMetadataExtractor, DefaultNoticeMetadataExtractor
from ted_sws.notice_metadata_processor.model.metadata import ExtractedMetadata
import xml.etree.ElementTree as ET


def check_if_xml_manifestation_is_eform(xml_manifestation: XMLManifestation) -> bool:
    """
        Check if the provided XML content is an Eform Notice document.
    """
    return ET.fromstring(xml_manifestation.object_data).tag == "TED_EXPORT"


def find_metadata_extractor_based_on_xml_manifestation(self,
                                                       xml_manifestation: XMLManifestation) -> NoticeMetadataExtractorABC:
    """
        Find the correct extractor based on the XML Manifestation
    """
    if check_if_xml_manifestation_is_eform(xml_manifestation):
        return EformsNoticeMetadataExtractor()
    else:
        return DefaultNoticeMetadataExtractor()


def find_metadata_normaliser_based_on_xml_manifestation(self,
                                                        xml_manifestation: XMLManifestation) -> NoticeMetadataNormaliserABC:
    """
        Find the correct extractor based on the XML Manifestation
    """
    if check_if_xml_manifestation_is_eform(xml_manifestation):
        return EformsNoticeMetadataNormaliser()
    else:
        return DefaultNoticeMetadataNormaliser()


def extract_notice_metadata(xml_manifestation: XMLManifestation,
                            metadata_extractor: NoticeMetadataExtractorABC) -> ExtractedMetadata:
    """
        Extract metadata using the correct extractor type
    """
    return metadata_extractor.extract_metadata(xml_manifestation)


def normalise_notice_metadata(extracted_metadata: ExtractedMetadata,
                              metadata_normaliser: NoticeMetadataNormaliserABC) -> NormalisedMetadata:
    """
        Normalise metadata using the correct normaliser type
    """
    return metadata_normaliser.normalise_metadata(extracted_metadata)


def extract_and_normalise_notice_metadata(xml_manifestation: XMLManifestation) -> NormalisedMetadata:
    """
        Extract and normalise metadata using the correct extractor and normaliser type
    """
    metadata_extractor = find_metadata_extractor_based_on_xml_manifestation(xml_manifestation)
    extracted_metadata = extract_notice_metadata(xml_manifestation, metadata_extractor)
    metadata_normaliser = find_metadata_normaliser_based_on_xml_manifestation(xml_manifestation)
    normalised_metadata = normalise_notice_metadata(extracted_metadata, metadata_normaliser)
    return normalised_metadata


def extract_and_normalise_notice_metadata_from_notice(notice: Notice) -> NormalisedMetadata:
    """
        Extract and normalise metadata using the correct extractor and normaliser type
    """
    xml_manifestation = notice.xml_manifestation
    return extract_and_normalise_notice_metadata(xml_manifestation)
