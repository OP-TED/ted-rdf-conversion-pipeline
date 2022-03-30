import datetime
from typing import List

from ted_sws.core.model.metadata import Metadata, CompositeTitle, LanguageTaggedString, EncodedValue


class ExtractedMetadata(Metadata):
    """
        Stores extracted metadata
    """
    title: List[CompositeTitle] = None
    notice_publication_number: str = None
    publication_date: str = None
    ojs_issue_number: str = None
    ojs_type: str = None
    city_of_buyer: List[LanguageTaggedString] = None
    name_of_buyer: List[LanguageTaggedString] = None
    original_language: str = None
    country_of_buyer: str = None
    type_of_buyer: EncodedValue = None
    eu_institution: str = None
    document_sent_date: str = None
    deadline_for_submission: str = None
    type_of_contract: EncodedValue = None
    type_of_procedure: EncodedValue = None
    extracted_document_type: EncodedValue = None
    extracted_form_number: str = None
    regulation: EncodedValue = None
    type_of_bid: EncodedValue = None
    award_criteria: EncodedValue = None
    common_procurement: List[EncodedValue] = None
    place_of_performance: List[EncodedValue] = None
    internet_address: str = None
    legal_basis_directive: str = None
    xml_schema: str = None
    xml_schema_version: str = None
    extracted_notice_type: str = None
