import abc
import xml.etree.ElementTree as ET
from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.notice_metadata_processor.adapters.xpath_registry import EformsXPathRegistry, DefaultXPathRegistry
from ted_sws.notice_metadata_processor.model.metadata import ExtractedMetadata


class NoticeMetadataExtractorABC(abc.ABC):

    @abc.abstractmethod
    def extract_metadata(self, xml_manifestation: XMLManifestation) -> ExtractedMetadata:
        pass


class DefaultNoticeMetadataExtractor(NoticeMetadataExtractorABC):

    def __init__(self):
        self.xpath_registry = DefaultXPathRegistry()

    def extract_metadata(self, xml_manifestation: XMLManifestation) -> ExtractedMetadata:
        pass


class EformsNoticeMetadataExtractor(NoticeMetadataExtractorABC):

    def __init__(self):
        self.xpath_registry = EformsXPathRegistry()

    def extract_metadata(self, xml_manifestation: XMLManifestation) -> ExtractedMetadata:
        pass


def parse_xml_manifestation(xml_manifestation: XMLManifestation) -> ET.Element:
    """
    Parsing XML manifestation and getting the root
    :return:
    """
    xml_manifestation_content = xml_manifestation.object_data
    return ET.fromstring(xml_manifestation_content)
