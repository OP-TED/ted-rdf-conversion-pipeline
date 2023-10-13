import abc

from ted_sws.core.model.metadata import NormalisedMetadata
from ted_sws.notice_metadata_processor.model.metadata import ExtractedMetadata


class NoticeMetadataNormaliserABC(abc.ABC):

    @abc.abstractmethod
    def normalise_metadata(self, extracted_metadata: ExtractedMetadata) -> NormalisedMetadata:
        """
            Normalise metadata
        """


class DefaultNoticeMetadataNormaliser(NoticeMetadataNormaliserABC):

    def normalise_metadata(self, extracted_metadata: ExtractedMetadata) -> NormalisedMetadata:
        pass


class EformsNoticeMetadataNormaliser(NoticeMetadataNormaliserABC):

    def normalise_metadata(self, extracted_metadata: ExtractedMetadata) -> NormalisedMetadata:
        pass
