import xml.etree.ElementTree as ET

from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.notice_metadata_processor.model.metadata import ExtractedMetadata





class NoticeMetadataExtractor:
    def __init__(self,xml_manifestation_metadata_extractor):
        self.xml_manifestation_metadata_extractor = xml_manifestation_metadata_extractor

    def extract_metadata(self, xml_manifestation: XMLManifestation):
        extracted_metadata = self.xml_manifestation_metadata_extractor(xml_manifestation)
        metadata: ExtractedMetadata = ExtractedMetadata()
        metadata.title = extracted_metadata.title
        metadata.notice_publication_number = extracted_metadata.notice_publication_number
        metadata.publication_date = extracted_metadata.publication_date
        metadata.ojs_type = extracted_metadata.ojs_type
        metadata.ojs_issue_number = extracted_metadata.ojs_issue_number
        metadata.city_of_buyer = extracted_metadata.city_of_buyer
        metadata.name_of_buyer = extracted_metadata.name_of_buyer
        metadata.original_language = extracted_metadata.original_language
        metadata.uri_list = extracted_metadata.uri_list
        metadata.country_of_buyer = extracted_metadata.country_of_buyer
        metadata.type_of_buyer = extracted_metadata.type_of_buyer
        metadata.eu_institution = extracted_metadata.eu_institution
        metadata.document_sent_date = extracted_metadata.document_sent_date
        metadata.type_of_contract = extracted_metadata.type_of_contract
        metadata.type_of_procedure = extracted_metadata.type_of_procedure
        metadata.extracted_document_type = extracted_metadata.extracted_document_type
        metadata.extracted_form_number = extracted_metadata.extracted_form_number
        metadata.regulation = extracted_metadata.regulation
        metadata.type_of_bid = extracted_metadata.type_of_bid
        metadata.award_criteria = extracted_metadata.award_criteria
        metadata.common_procurement = extracted_metadata.common_procurement
        metadata.place_of_performance = extracted_metadata.place_of_performance
        metadata.internet_address = extracted_metadata.internet_address
        metadata.legal_basis_directive = extracted_metadata.legal_basis_directive
        metadata.xml_schema = extracted_metadata.xml_schema
        metadata.xml_schema_version = extracted_metadata.xml_schema_version
        metadata.extracted_notice_type = extracted_metadata.extracted_notice_type
        return metadata


class NoticeExtractorMetadata:
    def __init__(self, xml_manifestation: XMLManifestation):
        self.xml_manifestation = xml_manifestation

    def _is_eform(self):
        """
            Check if the provided XML content is an Eform Notice document.
        """
        return ET.fromstring(self.xml_manifestation.object_data).tag == "TED_EXPORT"

    def extract(self) -> ExtractedMetadata:
        """
        Extract metadata using the correct extractor type
        """
        if self._is_eform():
            extractor = EformsNoticeMetadataExtractor()
        else:
            extractor = DefaultNoticeMetadataExtractor()
        return extractor.extract_metadata(self.xml_manifestation)
