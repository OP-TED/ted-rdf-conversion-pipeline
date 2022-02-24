from typing import List
from xml.etree.ElementTree import Element

from ted_sws.domain.model.metadata import ExtractedMetadata


def xpath_extract_data(elements: List[Element]) -> List[str]:
    return [element.text for element in elements]


def xpath_extract_attributes(elements: List[Element], attrib_key: str) -> List[str]:
    return [element.attrib[attrib_key] for element in elements]


class ExtractMetadata:
    """
      Extracting metadata from xml manifestation
    """

    def __init__(self, manifestation_root, namespaces):
        self.manifestation_root = manifestation_root
        self.namespaces = namespaces

    @property
    def title(self):
        title_text = xpath_extract_data(self.manifestation_root.findall(
            "manifestation_ns:TRANSLATION_SECTION/manifestation_ns:ML_TITLES/manifestation_ns:ML_TI_DOC[@LG='EN']/manifestation_ns:TI_TEXT/manifestation_ns:P",
            namespaces=self.namespaces))

        return xpath_extract_data(self.manifestation_root.findall(
            "manifestation_ns:TRANSLATION_SECTION/manifestation_ns:ML_TITLES/manifestation_ns:ML_TI_DOC[@LG='EN']/",
            namespaces=self.namespaces)[:2]) + title_text

    @property
    def notice_publication_number(self):
        return [self.manifestation_root.attrib["DOC_ID"]]

    @property
    def publication_date(self):
        return xpath_extract_data(self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:REF_OJS/manifestation_ns:DATE_PUB",
            namespaces=self.namespaces))

    @property
    def ojs_issue_number(self):
        return xpath_extract_data(self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:REF_OJS/manifestation_ns:NO_OJ",
            namespaces=self.namespaces))

    @property
    def city_of_buyer(self):
        return xpath_extract_data(self.manifestation_root.findall(
            "manifestation_ns:TRANSLATION_SECTION/manifestation_ns:ML_TITLES/manifestation_ns:ML_TI_DOC[@LG='EN']/manifestation_ns:TI_TOWN",
            namespaces=self.namespaces))

    @property
    def name_of_buyer(self):
        elements_found = self.manifestation_root.findall(
            "manifestation_ns:TRANSLATION_SECTION/manifestation_ns:ML_AA_NAMES/manifestation_ns:AA_NAME",
            namespaces=self.namespaces)
        if len(elements_found) == 1:
            return xpath_extract_data(elements=elements_found)
        else:
            return xpath_extract_data(
                elements=[next((element for element in elements_found if element.attrib["LG"] == "EN"), None)])

    @property
    def eu_institution(self):
        selected_element = self.manifestation_root.find(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:AA_AUTHORITY_TYPE",
            namespaces=self.namespaces)
        return [selected_element.text if selected_element.attrib["CODE"] == "5" else "-"]

    @property
    def country_of_buyer(self):
        return xpath_extract_attributes(self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:NOTICE_DATA/manifestation_ns:ISO_COUNTRY",
            namespaces=self.namespaces), attrib_key="VALUE")

    @property
    def original_language(self):
        return xpath_extract_data(self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:NOTICE_DATA/manifestation_ns:LG_ORIG",
            namespaces=self.namespaces))

    @property
    def document_sent_date(self):
        return xpath_extract_data(self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:DS_DATE_DISPATCH",
            namespaces=self.namespaces))

    @property
    def type_of_buyer(self):
        return xpath_extract_data(self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:AA_AUTHORITY_TYPE",
            namespaces=self.namespaces))

    @property
    def deadline_for_submission(self):
        return xpath_extract_data(self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:DT_DATE_FOR_SUBMISSION",
            namespaces=self.namespaces))

    @property
    def type_of_contract(self):
        return xpath_extract_data(self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:NC_CONTRACT_NATURE",
            namespaces=self.namespaces))

    @property
    def type_of_procedure(self):
        return xpath_extract_data(self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:PR_PROC",
            namespaces=self.namespaces))

    @property
    def notice_type(self):
        return xpath_extract_data(self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:TD_DOCUMENT_TYPE",
            namespaces=self.namespaces))

    @property
    def regulation(self):
        return xpath_extract_data(self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:RP_REGULATION",
            namespaces=self.namespaces))

    @property
    def type_of_bid(self):
        return xpath_extract_data(self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:TY_TYPE_BID",
            namespaces=self.namespaces))

    @property
    def award_criteria(self):
        return xpath_extract_data(self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:AC_AWARD_CRIT",
            namespaces=self.namespaces))

    @property
    def common_procurement(self):
        return xpath_extract_data(self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:NOTICE_DATA/manifestation_ns:ORIGINAL_CPV",
            namespaces=self.namespaces))

    @property
    def place_of_performance(self):
        return xpath_extract_attributes(elements=self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:NOTICE_DATA/manifestation_ns:PERFORMANCE_NUTS",
            namespaces=self.namespaces), attrib_key="CODE") or xpath_extract_attributes(
            elements=self.manifestation_root.findall(
                "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:NOTICE_DATA/nuts:PERFORMANCE_NUTS",
                namespaces=self.namespaces), attrib_key="CODE") or xpath_extract_attributes(
            elements=self.manifestation_root.findall(
                "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:NOTICE_DATA/manifestation_ns:ORIGINAL_NUTS",
                namespaces=self.namespaces), attrib_key="CODE")

    @property
    def internet_address(self):
        return xpath_extract_data(self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:NOTICE_DATA/manifestation_ns:IA_URL_GENERAL",
            namespaces=self.namespaces))

    @property
    def legal_basis_directive(self):
        return xpath_extract_attributes(elements=self.manifestation_root.findall(
            "manifestation_ns:CODED_DATA_SECTION/manifestation_ns:CODIF_DATA/manifestation_ns:DIRECTIVE",
            namespaces=self.namespaces), attrib_key="VALUE") or xpath_extract_attributes(
            elements=self.manifestation_root.findall(
                "manifestation_ns:FORM_SECTION/*/manifestation_ns:LEGAL_BASIS",
                namespaces=self.namespaces), attrib_key="VALUE") or xpath_extract_data(
            elements=self.manifestation_root.findall(
                "manifestation_ns:FORM_SECTION/*/manifestation_ns:LEGAL_BASIS_OTHER/manifestation_ns:P/manifestation_ns:FT", namespaces=self.namespaces))

    def to_metadata(self):
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
