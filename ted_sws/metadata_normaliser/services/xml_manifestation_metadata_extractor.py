from typing import List
import xml.etree.ElementTree as ET
from io import StringIO

from ted_sws.domain.model.metadata import ExtractedMetadata


def extract_text_from_element(element: ET.Element) -> str:
    """
    Extract text from an element in the XML structure
    :param element:
    :return: str
    """
    if element is not None:
        return element.text


def extract_attribute_from_element(element: ET.Element, attrib_key: str) -> str:
    """
    Extract attribute value from an element in the XML structure
    :param element:
    :param attrib_key:
    :return:
    """
    if element is not None:
        return element.attrib[attrib_key]


def extract_code_and_value_from_element(element: ET.Element) -> EncodedValue:
    """
    Extract code attribute and text values from an element in the XML structure
    :param element:
    :return:
    """
    if element is not None:
        return EncodedValue(code=extract_attribute_from_element(element=element, attrib_key="CODE"),
                            value=extract_text_from_element(element=element))


class XMLManifestationMetadataExtractor:
    """
      Extracting metadata from xml manifestation
    """

    def __init__(self, manifestation_root, namespaces):
        self.manifestation_root = manifestation_root
        self.namespaces = namespaces

    @property
    def title(self):
        title_translations = []
        title_elements = self.manifestation_root.findall(
            "manifestation_ns:TRANSLATION_SECTION/manifestation_ns:ML_TITLES/",
            namespaces=self.namespaces)
        for title in title_elements:
            language = title.find(".").attrib["LG"]
            title_country = LanguageTaggedString(
                text=extract_text_from_element(
                    element=title.find("manifestation_ns:TI_CY", namespaces=self.namespaces)),
                language=language)
            title_city = LanguageTaggedString(
                text=extract_text_from_element(
                    element=title.find("manifestation_ns:TI_TOWN", namespaces=self.namespaces)),
                language=language)

            title_text = LanguageTaggedString(
                text=extract_text_from_element(element=title.find("manifestation_ns:TI_TEXT/manifestation_ns:P",
                                                                  namespaces=self.namespaces)) or extract_text_from_element(
                    element=title.find("manifestation_ns:TI_TEXT", namespaces=self.namespaces)),
                language=language)
            title_translations.append(
                CompositeTitle(title=title_text, title_city=title_city, title_country=title_country))

        return title_translations

    @property
    def notice_publication_number(self):
        return self.manifestation_root.attrib["DOC_ID"]

    @property
    def publication_date(self):
        return extract_text_from_element(element=self.manifestation_root.find(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:REF_OJS/manifestation_ns:DATE_PUB",
            namespaces=self.namespaces))

    @property
    def ojs_type(self):
        return extract_text_from_element(element=self.manifestation_root.find(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:REF_OJS/manifestation_ns:COLL_OJ",
            namespaces=self.namespaces))

    @property
    def ojs_issue_number(self):
        return extract_text_from_element(element=self.manifestation_root.find(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:REF_OJS/manifestation_ns:NO_OJ",
            namespaces=self.namespaces))

    @property
    def city_of_buyer(self):
        return [title.title_city for title in self.title]

    @property
    def name_of_buyer(self):
        buyer_name_elements = self.manifestation_root.findall(
            "manifestation_ns:TRANSLATION_SECTION/manifestation_ns:ML_AA_NAMES/",
            namespaces=self.namespaces)

        return [LanguageTaggedString(text=extract_text_from_element(element=buyer_name.find(".")),
                                     language=extract_attribute_from_element(element=buyer_name.find("."),
                                                                             attrib_key="LG")) for
                buyer_name in buyer_name_elements]

    @property
    def eu_institution(self):
        return self.type_of_buyer.value if self.type_of_buyer.code == "5" else "-"

    @property
    def country_of_buyer(self):
        return extract_attribute_from_element(element=self.manifestation_root.find(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:NOTICE_DATA/manifestation_ns:ISO_COUNTRY",
            namespaces=self.namespaces), attrib_key="VALUE")

    @property
    def original_language(self):
        return extract_text_from_element(element=self.manifestation_root.find(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:NOTICE_DATA/manifestation_ns:LG_ORIG",
            namespaces=self.namespaces))

    @property
    def document_sent_date(self):
        return extract_text_from_element(element=self.manifestation_root.find(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:DS_DATE_DISPATCH",
            namespaces=self.namespaces))

    @property
    def type_of_buyer(self):
        return extract_code_and_value_from_element(element=self.manifestation_root.find(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:AA_AUTHORITY_TYPE",
            namespaces=self.namespaces))

    @property
    def deadline_for_submission(self):
        return extract_text_from_element(element=self.manifestation_root.find(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:DT_DATE_FOR_SUBMISSION",
            namespaces=self.namespaces))

    @property
    def type_of_contract(self):
        return extract_code_and_value_from_element(element=self.manifestation_root.find(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:NC_CONTRACT_NATURE",
            namespaces=self.namespaces))

    @property
    def type_of_procedure(self):
        return extract_code_and_value_from_element(element=self.manifestation_root.find(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:PR_PROC",
            namespaces=self.namespaces))

    @property
    def notice_type(self):
        return extract_code_and_value_from_element(element=self.manifestation_root.find(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:TD_DOCUMENT_TYPE",
            namespaces=self.namespaces))

    @property
    def regulation(self):
        return extract_code_and_value_from_element(element=self.manifestation_root.find(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:RP_REGULATION",
            namespaces=self.namespaces))

    @property
    def type_of_bid(self):
        return extract_code_and_value_from_element(element=self.manifestation_root.find(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:TY_TYPE_BID",
            namespaces=self.namespaces))

    @property
    def award_criteria(self):
        return extract_code_and_value_from_element(element=self.manifestation_root.find(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:AC_AWARD_CRIT",
            namespaces=self.namespaces))

    @property
    def common_procurement(self):
        common_procurement_elements = self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:NOTICE_DATA/manifestation_ns:ORIGINAL_CPV",
            namespaces=self.namespaces)
        return [extract_code_and_value_from_element(element=element) for element in common_procurement_elements]

    @property
    def place_of_performance(self):
        place_of_performance_elements = self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:NOTICE_DATA/manifestation_ns:PERFORMANCE_NUTS",
            namespaces=self.namespaces) or self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:NOTICE_DATA/nuts:PERFORMANCE_NUTS",
            namespaces=self.namespaces) or self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:NOTICE_DATA/manifestation_ns:ORIGINAL_NUTS",
            namespaces=self.namespaces)

        return [extract_code_and_value_from_element(element=element) for element in place_of_performance_elements]

    @property
    def internet_address(self):
        return extract_text_from_element(element=self.manifestation_root.find(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:NOTICE_DATA/manifestation_ns:IA_URL_GENERAL",
            namespaces=self.namespaces))

    @property
    def legal_basis_directive(self):
        return extract_attribute_from_element(element=self.manifestation_root.find(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:DIRECTIVE",
            namespaces=self.namespaces), attrib_key="VALUE") or extract_attribute_from_element(
            element=self.manifestation_root.find(
                "manifestation_ns:FORM_SECTION/*/manifestation_ns:LEGAL_BASIS",
                namespaces=self.namespaces), attrib_key="VALUE") or extract_text_from_element(
            element=self.manifestation_root.find(
                "manifestation_ns:FORM_SECTION/*/manifestation_ns:LEGAL_BASIS_OTHER/manifestation_ns:P/manifestation_ns:FT",
                namespaces=self.namespaces))

    def to_metadata(self) -> ExtractedMetadata:
        """
         Creating extracted metadata
        :return:
        """
        metadata = ExtractedMetadata()
        metadata.title = self.title
        metadata.notice_publication_number = self.notice_publication_number
        metadata.publication_date = self.publication_date
        metadata.ojs_issue_number = self.ojs_issue_number
        metadata.city_of_buyer = self.city_of_buyer
        metadata.name_of_buyer = self.name_of_buyer
        metadata.original_language = self.original_language
        metadata.country_of_buyer = self.country_of_buyer
        metadata.type_of_buyer = self.type_of_buyer
        metadata.eu_institution = self.eu_institution
        metadata.document_sent_date = self.document_sent_date
        metadata.type_of_contract = self.type_of_contract
        metadata.type_of_procedure = self.type_of_procedure
        metadata.notice_type = self.notice_type
        metadata.regulation = self.regulation
        metadata.type_of_bid = self.type_of_bid
        metadata.award_criteria = self.award_criteria
        metadata.common_procurement = self.common_procurement
        metadata.place_of_performance = self.place_of_performance
        metadata.internet_address = self.internet_address
        metadata.legal_basis_directive = self.legal_basis_directive
        return metadata
