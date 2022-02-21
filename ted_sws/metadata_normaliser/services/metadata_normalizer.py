import abc

from ted_sws.domain.model.manifestation import XMLManifestation
from ted_sws.domain.model.metadata import NormalisedMetadata
from ted_sws.domain.model.notice import Notice


class MetadataNormalizerABC(abc.ABC):
    """
    Abstract class for notice metadata normalising process
    """

    @abc.abstractmethod
    def normalise_metadata(self) -> NormalisedMetadata:
        """
        Method to normalise metadata

        """


class MetadataNormaliser(MetadataNormalizerABC):
    """

    """

    def __init__(self, notice: Notice):
        self.notice = notice

    def _extract_metadata(self, xml_manifestation: XMLManifestation) -> dict:
        pass

    def normalise_metadata(self):
        metadata = self._extract_metadata(xml_manifestation=self.notice)


