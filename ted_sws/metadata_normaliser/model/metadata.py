from typing import List, Optional

from pydantic.annotated_types import NamedTuple

from ted_sws.domain.model.metadata import Metadata


class LanguageTaggedString(NamedTuple):
    """
    Holds strings with language tag
    """
    text: str = None
    language: str = None


class CompositeTitle(Metadata):
    """
    Compose title
    """
    title: LanguageTaggedString = None
    title_city: LanguageTaggedString = None
    title_country: LanguageTaggedString = None


class EncodedValue(NamedTuple):
    """
    Holds code and value
    """
    code: str = None
    value: str = None


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
    extracted_notice_type: EncodedValue = None
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
