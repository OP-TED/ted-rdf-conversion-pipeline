import abc

from ted_sws.domain.model.metadata import NormalisedMetadata
from ted_sws.domain.model.notice import Notice
from ted_sws.metadata_normaliser.services.xml_manifestation_metadata_extractor import XMLManifestationMetadataExtractor


class MetadataNormaliserABC(abc.ABC):
    """
    Abstract class for notice metadata normalising process
    """

    @abc.abstractmethod
    def normalise_metadata(self) -> NormalisedMetadata:
        """
        Method to normalise metadata

        """


class MetadataNormaliser(MetadataNormaliserABC):
    """
        Metadata normaliser
    """

    def __init__(self, notice: Notice):
        self.notice = notice

    def normalise_metadata(self):
        """
            Method that is normalising the metadata
        :return:
        """
        metadata = XMLManifestationMetadataExtractor(
            xml_manifestation=self.notice.xml_manifestation).to_metadata().dict()
        # TODO delete this when the nomalised meatdata strucuture is defined
        metadata["title"] = metadata["title"][0]['title'].text
        self.notice.set_normalised_metadata(normalised_metadata=NormalisedMetadata(**metadata))
