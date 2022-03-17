import abc

from ted_sws.domain.model.metadata import NormalisedMetadata
from ted_sws.domain.model.notice import Notice
from ted_sws.metadata_normaliser.model.metadata import ExtractedMetadata
from ted_sws.metadata_normaliser.services.xml_manifestation_metadata_extractor import XMLManifestationMetadataExtractor
from ted_sws.data_manager.adapters.notice_repository import NoticeRepositoryABC


def normalise_notice(notice: Notice) -> Notice:
    """
        Given a notice object, normalise metadata and return the updated object
    :param notice:
    :return:
    """
    extracted_metadata = XMLManifestationMetadataExtractor(
        xml_manifestation=notice.xml_manifestation).to_metadata()
    normalised_metadata = ExtractedMetadataNormaliser(extracted_metadata).to_metadata()
    notice.set_normalised_metadata(normalised_metadata)
    return notice


def normalise_notice_by_id(notice_id: str, notice_repository: NoticeRepositoryABC) -> Notice:
    """
        Given a notice id, find the notice in the database, normalise its metadata, and store the updated state.
    :param notice_id:
    :param notice_repository:
    :return:
    """
    notice: Notice = notice_repository.get(reference=notice_id)
    if notice is None:
        raise ValueError('Notice, with "%s" notice_id, was not found' % notice_id)

    return normalise_notice(notice)


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


class ExtractedMetadataNormaliser:

    def __init__(self, extracted_metadata: ExtractedMetadata):
        # TODO:
        ...

    def to_metadata(self) -> NormalisedMetadata:
        """
            Generate the normalised metadata
        :return:
        """
        ...
