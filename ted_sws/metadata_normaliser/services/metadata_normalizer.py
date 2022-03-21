import abc
import datetime

from ted_sws.data_manager.adapters.notice_repository import NoticeRepositoryABC
from ted_sws.domain.model.metadata import NormalisedMetadata, LanguageTaggedString
from ted_sws.domain.model.notice import Notice
from ted_sws.metadata_normaliser.model.metadata import ExtractedMetadata
from ted_sws.metadata_normaliser.services.xml_manifestation_metadata_extractor import XMLManifestationMetadataExtractor

JOIN_SEP = " :: "


def normalise_notice(notice: Notice) -> Notice:
    """
        Given a notice object, normalise metadata and return the updated object
    :param notice:
    :return:
    """
    MetadataNormaliser(notice=notice).normalise_metadata()
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
        extracted_metadata = XMLManifestationMetadataExtractor(
            xml_manifestation=self.notice.xml_manifestation).to_metadata()
        normalised_metadata = ExtractedMetadataNormaliser(extracted_metadata).to_metadata()
        self.notice.set_normalised_metadata(normalised_metadata)


class ExtractedMetadataNormaliser:

    def __init__(self, extracted_metadata: ExtractedMetadata):
        self.extracted_metadata = extracted_metadata

    def to_metadata(self) -> NormalisedMetadata:
        """
            Generate the normalised metadata
        :return:
        """
        emd = self.extracted_metadata
        metadata = {
            "title": [k.title for k in emd.title],
            "long_title": [
                LanguageTaggedString(text=JOIN_SEP.join(
                    [
                        k.title_country.text,
                        k.title_city.text,
                        k.title.text
                    ]),
                    language=k.title.language) for k in emd.title
            ],
            "notice_publication_number": emd.notice_publication_number,
            "publication_date": datetime.datetime.strptime(
                emd.publication_date, '%Y%m%d'
            ) if emd.publication_date is not None else None,
            "ojs_issue_number": emd.ojs_issue_number if emd.ojs_issue_number is not None else "",
            "ojs_type": emd.ojs_type if emd.ojs_type is not None else "",
            "city_of_buyer": [k for k in emd.city_of_buyer],
            "name_of_buyer": [k for k in emd.name_of_buyer],
            "original_language": emd.original_language,
            "country_of_buyer": emd.country_of_buyer,
            "eu_institution": True if emd.eu_institution in ['+', 'true'] else False,
            "document_sent_date": datetime.datetime.strptime(
                emd.document_sent_date, '%Y%m%d'
            ) if emd.document_sent_date is not None else None,
            "deadline_for_submission": datetime.datetime.strptime(
                emd.deadline_for_submission, '%Y%m%d'
            ) if emd.deadline_for_submission is not None else None,
            "notice_type": emd.notice_type.value,
            "form_type": '',
            "place_of_performance": [k.value for k in emd.place_of_performance],
            "legal_basis_directive": emd.legal_basis_directive if emd.legal_basis_directive is not None else ""
        }

        return NormalisedMetadata(**metadata)
