from typing import Optional
import xml.etree.ElementTree as ET

from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.core.model.metadata import NormalisedMetadata, NormalisedMetadataView
from ted_sws.core.model.notice import Notice
from ted_sws.data_manager.adapters.notice_repository import NoticeRepositoryABC
from ted_sws.notice_metadata_processor.adapters.notice_metadata_extractor import NoticeMetadataExtractorABC, \
    EformsNoticeMetadataExtractor, DefaultNoticeMetadataExtractor
from ted_sws.notice_metadata_processor.adapters.notice_metadata_normaliser import NoticeMetadataNormaliserABC, \
    EformsNoticeMetadataNormaliser, DefaultNoticeMetadataNormaliser, ENGLISH_LANGUAGE_TAG, LONG_TITLE_KEY, TITLE_KEY, \
    BUYER_NAME_KEY, BUYER_CITY_KEY
from ted_sws.notice_metadata_processor.model.metadata import ExtractedMetadata


def check_if_xml_manifestation_is_eform(xml_manifestation: XMLManifestation) -> bool:
    """
        Check if the provided XML content is an Eform Notice document.
    """
    return "TED_EXPORT" not in ET.fromstring(xml_manifestation.object_data).tag


def find_metadata_extractor_based_on_xml_manifestation(
        xml_manifestation: XMLManifestation) -> NoticeMetadataExtractorABC:
    """
        Find the correct extractor based on the XML Manifestation
    """
    if check_if_xml_manifestation_is_eform(xml_manifestation):
        return EformsNoticeMetadataExtractor(xml_manifestation=xml_manifestation)
    else:
        return DefaultNoticeMetadataExtractor(xml_manifestation=xml_manifestation)


def find_metadata_normaliser_based_on_xml_manifestation(
        xml_manifestation: XMLManifestation) -> NoticeMetadataNormaliserABC:
    """
        Find the correct extractor based on the XML Manifestation
    """
    if check_if_xml_manifestation_is_eform(xml_manifestation):
        return EformsNoticeMetadataNormaliser()
    else:
        return DefaultNoticeMetadataNormaliser()


def extract_notice_metadata(metadata_extractor: NoticeMetadataExtractorABC) -> ExtractedMetadata:
    """
        Extract metadata using the correct extractor type
    """
    return metadata_extractor.extract_metadata()


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
    extracted_metadata = extract_notice_metadata(metadata_extractor)
    metadata_normaliser = find_metadata_normaliser_based_on_xml_manifestation(xml_manifestation)
    normalised_metadata = normalise_notice_metadata(extracted_metadata, metadata_normaliser)
    return normalised_metadata


def extract_and_normalise_notice_metadata_from_notice(notice: Notice) -> NormalisedMetadata:
    """
        Extract and normalise metadata using the correct extractor and normaliser type
    """
    xml_manifestation = notice.xml_manifestation
    return extract_and_normalise_notice_metadata(xml_manifestation)


def normalise_notice(notice: Notice) -> Notice:
    """
        Given a notice object, normalise metadata and return the updated object
    :param notice:
    :return:
    """
    normalised_metadata = extract_and_normalise_notice_metadata_from_notice(notice=notice)
    notice.set_normalised_metadata(normalised_metadata)
    return notice


def normalise_notice_by_id(notice_id: str, notice_repository: NoticeRepositoryABC) -> Notice:
    """
        Given a notice id, find the notice in the database, normalise its metadata, and store the updated state.
    :param notice_id:
    :param notice_repository:
    :return:
    """
    notice: Notice = notice_repository.get(reference=notice_id)
    if notice is None:
        raise ValueError('Notice, with "%s" notice_id, was not found' % notice_id)

    return normalise_notice(notice)


def create_normalised_metadata_view(normalised_metadata: NormalisedMetadata) -> Optional[NormalisedMetadataView]:
    if normalised_metadata:
        english_titles = [title.text for title in normalised_metadata.title if title.language == ENGLISH_LANGUAGE_TAG]
        title = "no_english_title" if len(english_titles) == 0 else english_titles[0]
        english_long_titles = [title.text for title in normalised_metadata.long_title
                               if title.language == ENGLISH_LANGUAGE_TAG]
        long_title = "no_english_long_title" if len(english_long_titles) == 0 else english_long_titles[0]
        city_of_buyer = None
        if normalised_metadata.city_of_buyer:
            english_city_of_buyer = [city.text for city in normalised_metadata.city_of_buyer
                                     if city.language == ENGLISH_LANGUAGE_TAG]
            city_of_buyer = "no_english_city_of_buyer" if len(english_city_of_buyer) == 0 else english_city_of_buyer[0]

        name_of_buyer = None
        if normalised_metadata.name_of_buyer:
            english_name_of_buyer = [name.text for name in normalised_metadata.name_of_buyer
                                     if name.language == ENGLISH_LANGUAGE_TAG]
            name_of_buyer = "no_english_city_of_buyer" if len(english_name_of_buyer) == 0 else english_name_of_buyer[0]
        normalised_metadata_dict = normalised_metadata.dict(exclude={TITLE_KEY: True, LONG_TITLE_KEY: True,
                                                                           BUYER_NAME_KEY: True, BUYER_CITY_KEY: True})
        return NormalisedMetadataView(title=title, long_title=long_title,
                                      name_of_buyer=name_of_buyer, city_of_buyer=city_of_buyer,
                                      **normalised_metadata_dict)
    return None


