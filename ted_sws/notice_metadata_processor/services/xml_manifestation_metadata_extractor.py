import xml.etree.ElementTree as ET
from io import StringIO

from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.notice_metadata_processor.model.metadata import ExtractedMetadata, LanguageTaggedString, CompositeTitle, \
    EncodedValue
from ted_sws.notice_metadata_processor.services.xpath_registry import XpathRegistry


class XMLManifestationMetadataExtractor:
    """
      Extracts metadata from an XML manifestation.
    """

    def __init__(self, xml_manifestation: XMLManifestation):
        self.xml_manifestation = xml_manifestation
        self.manifestation_root = self._parse_manifestation()
        self.namespaces = self._get_normalised_namespaces()
        self.xpath_registry = XpathRegistry()

    @property
    def title(self):
        title_translations = []
        title_elements = self.manifestation_root.findall(
            self.xpath_registry.xpath_title_elements,
            namespaces=self.namespaces)
        for title in title_elements:
            language = title.find(".").attrib["LG"]
            title_country = LanguageTaggedString(
                text=extract_text_from_element(
                    element=title.find(self.xpath_registry.xpath_title_country, namespaces=self.namespaces)),
                language=language)
            title_city = LanguageTaggedString(
                text=extract_text_from_element(
                    element=title.find(self.xpath_registry.xpath_title_town, namespaces=self.namespaces)),
                language=language)

            title_text = LanguageTaggedString(
                text=extract_text_from_element(element=title.find(self.xpath_registry.xpath_title_text_first,
                                                                  namespaces=self.namespaces)) or extract_text_from_element(
                    element=title.find(self.xpath_registry.xpath_title_text_second, namespaces=self.namespaces)),
                language=language)
            title_translations.append(
                CompositeTitle(title=title_text, title_city=title_city, title_country=title_country))

        return title_translations

    @property
    def notice_publication_number(self):
        return self.manifestation_root.get("DOC_ID")

    @property
    def publication_date(self):
        return extract_text_from_element(element=self.manifestation_root.find(
            self.xpath_registry.xpath_publication_date,
            namespaces=self.namespaces))

    @property
    def ojs_type(self):
        return extract_text_from_element(element=self.manifestation_root.find(
            self.xpath_registry.xpath_ojs_type,
            namespaces=self.namespaces))

    @property
    def ojs_issue_number(self):
        return extract_text_from_element(element=self.manifestation_root.find(
            self.xpath_registry.xpath_ojs_issue_number,
            namespaces=self.namespaces))

    @property
    def city_of_buyer(self):
        return [title.title_city for title in self.title]

    @property
    def name_of_buyer(self):
        buyer_name_elements = self.manifestation_root.findall(
            self.xpath_registry.xpath_name_of_buyer_elements,
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
            self.xpath_registry.xpath_country_of_buyer,
            namespaces=self.namespaces), attrib_key="VALUE")

    @property
    def original_language(self):
        return extract_text_from_element(element=self.manifestation_root.find(
            self.xpath_registry.xpath_original_language,
            namespaces=self.namespaces))

    @property
    def document_sent_date(self):
        return extract_text_from_element(element=self.manifestation_root.find(
            self.xpath_registry.xpath_document_sent_date,
            namespaces=self.namespaces))

    @property
    def type_of_buyer(self):
        return extract_code_and_value_from_element(element=self.manifestation_root.find(
            self.xpath_registry.xpath_type_of_buyer,
            namespaces=self.namespaces))

    @property
    def deadline_for_submission(self):
        return extract_text_from_element(element=self.manifestation_root.find(
            self.xpath_registry.xpath_deadline_for_submission,
            namespaces=self.namespaces))

    @property
    def type_of_contract(self):
        return extract_code_and_value_from_element(element=self.manifestation_root.find(
            self.xpath_registry.xpath_type_of_contract,
            namespaces=self.namespaces))

    @property
    def type_of_procedure(self):
        return extract_code_and_value_from_element(element=self.manifestation_root.find(
            self.xpath_registry.xpath_type_of_procedure,
            namespaces=self.namespaces))

    @property
    def extracted_document_type(self):
        return extract_code_and_value_from_element(element=self.manifestation_root.find(
            self.xpath_registry.xpath_document_type,
            namespaces=self.namespaces))

    @property
    def extracted_form_number(self):
        return extract_attribute_from_element(element=self.manifestation_root.find(
            self.xpath_registry.xpath_form_number,
            namespaces=self.namespaces), attrib_key="FORM")

    @property
    def regulation(self):
        return extract_code_and_value_from_element(element=self.manifestation_root.find(
            self.xpath_registry.xpath_regulation,
            namespaces=self.namespaces))

    @property
    def type_of_bid(self):
        return extract_code_and_value_from_element(element=self.manifestation_root.find(
            self.xpath_registry.xpath_type_of_bid,
            namespaces=self.namespaces))

    @property
    def award_criteria(self):
        return extract_code_and_value_from_element(element=self.manifestation_root.find(
            self.xpath_registry.xpath_award_criteria,
            namespaces=self.namespaces))

    @property
    def common_procurement(self):
        common_procurement_elements = self.manifestation_root.findall(
            self.xpath_registry.xpath_common_procurement_elements,
            namespaces=self.namespaces)
        return [extract_code_and_value_from_element(element=element) for element in common_procurement_elements]

    @property
    def place_of_performance(self):
        place_of_performance_elements = self.manifestation_root.findall(
            self.xpath_registry.xpath_place_of_performance_first,
            namespaces=self.namespaces) or self.manifestation_root.findall(
            self.xpath_registry.xpath_place_of_performance_second,
            namespaces=self.namespaces) or self.manifestation_root.findall(
            self.xpath_registry.xpath_place_of_performance_third,
            namespaces=self.namespaces)

        return [extract_code_and_value_from_element(element=element) for element in place_of_performance_elements]

    @property
    def internet_address(self):
        return extract_text_from_element(element=self.manifestation_root.find(
            self.xpath_registry.xpath_internet_address,
            namespaces=self.namespaces))

    @property
    def legal_basis_directive(self):
        return extract_attribute_from_element(element=self.manifestation_root.find(
            self.xpath_registry.xpath_legal_basis_directive_first,
            namespaces=self.namespaces), attrib_key="VALUE") or extract_attribute_from_element(
            element=self.manifestation_root.find(
                self.xpath_registry.xpath_legal_basis_directive_second,
                namespaces=self.namespaces), attrib_key="VALUE") or extract_text_from_element(
            element=self.manifestation_root.find(
                self.xpath_registry.xpath_legal_basis_directive_third,
                namespaces=self.namespaces))

    @property
    def xml_schema(self):
        xsi_namespace = self.namespaces.get("xsi")
        xml_schema_attribute = f"{ {xsi_namespace} }schemaLocation".replace("'", "")
        return self.manifestation_root.get(xml_schema_attribute) if xsi_namespace else None

    @property
    def xml_schema_version(self):
        return self.manifestation_root.get("VERSION") or extract_attribute_from_element(
            element=self.manifestation_root.find(
                self.xpath_registry.xpath_form_number,
                namespaces=self.namespaces), attrib_key="VERSION")

    @property
    def extracted_notice_type(self):
        return extract_attribute_from_element(element=self.manifestation_root.find(
            self.xpath_registry.xpath_notice_type,
            namespaces=self.namespaces), attrib_key="TYPE")

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
        metadata.extracted_document_type = self.extracted_document_type
        metadata.extracted_form_number = self.extracted_form_number
        metadata.regulation = self.regulation
        metadata.type_of_bid = self.type_of_bid
        metadata.award_criteria = self.award_criteria
        metadata.common_procurement = self.common_procurement
        metadata.place_of_performance = self.place_of_performance
        metadata.internet_address = self.internet_address
        metadata.legal_basis_directive = self.legal_basis_directive
        metadata.xml_schema = self.xml_schema
        metadata.xml_schema_version = self.xml_schema_version
        metadata.extracted_notice_type = self.extracted_notice_type
        return metadata

    def _parse_manifestation(self):
        """
        Parsing XML manifestation and getting the root
        :return:
        """
        xml_manifestation_content = self.xml_manifestation.object_data
        return ET.fromstring(xml_manifestation_content)

    def _get_normalised_namespaces(self):
        """
        Get normalised namespaces from XML manifestation
        :return:
        """
        namespaces = dict([node for _, node in ET.iterparse(source=StringIO(self.xml_manifestation.object_data),
                                                            events=['start-ns'])])

        namespaces["manifestation_ns"] = namespaces.pop("") if "" in namespaces.keys() else ""

        tmp_dict = namespaces.copy()
        items = tmp_dict.items()
        for key, value in items:
            if value.endswith("nuts"):
                namespaces["nuts"] = namespaces.pop(key)

        if "nuts" not in namespaces.keys():
            namespaces.update({"nuts": "no_nuts"})

        return namespaces


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
        return element.get(attrib_key)


def extract_code_and_value_from_element(element: ET.Element) -> EncodedValue:
    """
    Extract code attribute and text values from an element in the XML structure
    :param element:
    :return:
    """
    if element is not None:
        return EncodedValue(code=extract_attribute_from_element(element=element, attrib_key="CODE"),
                            value=extract_text_from_element(element=element))
