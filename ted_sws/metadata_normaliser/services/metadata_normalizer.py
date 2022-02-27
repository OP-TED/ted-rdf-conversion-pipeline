import abc

from ted_sws.domain.model.metadata import NormalisedMetadata
from ted_sws.domain.model.notice import Notice
from ted_sws.metadata_normaliser.services.extract_metadata import MetadataExtractor


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
        metadata = MetadataExtractor(notice=self.notice).extract_metadata().dict()
        #TODO delete this when the nomalised meatdata strucuture is defined
        metadata["title"] = " ".join(metadata["title"])
        self.notice.set_normalised_metadata(normalised_metadata=NormalisedMetadata(**metadata))
