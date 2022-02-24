from ted_sws.domain.model.metadata import NormalisedMetadata
from ted_sws.domain.model.notice import Notice
import xml.etree.ElementTree as ET
from io import StringIO

from ted_sws.metadata_normaliser.services import ExtractMetadata


class MetadataExtractor:
    """
        Metadata extractor
    """

    def __init__(self, notice: Notice):
        self.notice = notice

    def extract_metadata(self) -> NormalisedMetadata:
        """
        Method to extract metadata from xml manifestation
        :param self:
        :return: NormalisedMetadata
        """
        xml_manifestation_content = self.notice.xml_manifestation.object_data
        manifestation_root = ET.fromstring(xml_manifestation_content)
        namespaces = dict([node for _, node in ET.iterparse(source=StringIO(xml_manifestation_content),
                                                            events=['start-ns'])])

        namespaces["manifestation_ns"] = namespaces.pop("")

        for key, value in namespaces.items():
            if value.endswith("nuts"):
                namespaces["nuts"] = namespaces.pop(key)

        if "nuts" not in namespaces.keys():
            namespaces.update({"nuts": "no_nuts"})

        return ExtractMetadata(manifestation_root=manifestation_root, namespaces=namespaces).to_metadata()
