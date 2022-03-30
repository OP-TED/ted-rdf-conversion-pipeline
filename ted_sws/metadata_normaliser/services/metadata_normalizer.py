import abc
import datetime

import pandas as pd

from ted_sws.core.service.metadata_constraints import filter_df_by_variables
from ted_sws.data_manager.adapters.notice_repository import NoticeRepositoryABC
from ted_sws.core.model.metadata import NormalisedMetadata, LanguageTaggedString
from ted_sws.core.model.notice import Notice
from ted_sws.metadata_normaliser.model.metadata import ExtractedMetadata
from ted_sws.metadata_normaliser.services.xml_manifestation_metadata_extractor import XMLManifestationMetadataExtractor
from ted_sws.metadata_normaliser.resources.mapping_files_registry import MappingFilesRegistry

from typing import Dict, Tuple

JOIN_SEP = " :: "
MERGING_COLUMN = "eforms_subtype"


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

    @classmethod
    def get_map_value(cls, mapping: Dict, value: str) -> str:
        """
        Returns mapped URI for value
        :param mapping:
        :param value:
        :return:
        """
        entry_list = [element for element in mapping['results']['bindings'] if element['code']['value'] == value]
        entry = None
        if entry_list:
            entry = entry_list[0]

        return entry['conceptURI']['value'] if entry else None

    @classmethod
    def normalise_legal_basis_value(cls, value: str) -> str:
        """
        Transforms and returns Legal Basis value
        :param mapping:
        :param value:
        :return:
        """
        pattern = "3{year}L{number}"
        normalised_value = value
        parts = value.split("/")
        if len(parts) > 1:
            normalised_value = pattern.format(year=parts[0], number=parts[1].rjust(4, "0"))

        return normalised_value

    @classmethod
    def normalise_form_number(cls, value: str) -> str:
        """
        Normalise form number to be F{number} format
        :param value:
        :return:
        """
        if value and not value.startswith("F"):
            return "F" + value
        return value

    @classmethod
    def get_form_type_and_notice_type(cls, ef_map: pd.DataFrame, sf_map: pd.DataFrame, form_number: str,
                                      extracted_notice_type: str, legal_basis: str, document_type_code: str) -> Tuple:
        """
        Returns notice_type and form_type
        :param ef_map:
        :param sf_map:
        :param form_number:
        :param extracted_notice_type:
        :param legal_basis:
        :param document_type_code:
        :return:
        """
        mapping_df = pd.merge(sf_map, ef_map, on=MERGING_COLUMN, how="left")
        filtered_df = filter_df_by_variables(df=mapping_df, form_number=form_number,
                                             sf_notice_type=extracted_notice_type, legal_basis=legal_basis,
                                             document_code=document_type_code)
        form_type = filtered_df["form_type"].values[0]
        notice_type = filtered_df["eform_notice_type"].values[0]
        return form_type, notice_type

    def to_metadata(self) -> NormalisedMetadata:
        """
            Generate the normalised metadata
        :return:
        """

        mapping_registry = MappingFilesRegistry()
        countries_map = mapping_registry.countries
        form_type_map = mapping_registry.form_type
        languages_map = mapping_registry.languages
        legal_basis_map = mapping_registry.legal_basis
        notice_type_map = mapping_registry.notice_type
        nuts_map = mapping_registry.nuts
        standard_forms_map = mapping_registry.sf_notice_df
        eforms_map = mapping_registry.ef_notice_df
        form_type, notice_type = self.get_form_type_and_notice_type(sf_map=standard_forms_map, ef_map=eforms_map,
                                                                    extracted_notice_type=self.extracted_metadata.extracted_notice_type,
                                                                    form_number=self.normalise_form_number(
                                                                        self.extracted_metadata.extracted_form_number),
                                                                    legal_basis=self.normalise_legal_basis_value(
                                                                        self.extracted_metadata.legal_basis_directive),
                                                                    document_type_code=self.extracted_metadata.extracted_document_type.code)

        extracted_metadata = self.extracted_metadata

        metadata = {
            "title": [title.title for title in extracted_metadata.title],
            "long_title": [
                LanguageTaggedString(text=JOIN_SEP.join(
                    [
                        title.title_country.text,
                        title.title_city.text,
                        title.title.text
                    ]),
                    language=title.title.language) for title in extracted_metadata.title
            ],
            "notice_publication_number": extracted_metadata.notice_publication_number,
            "publication_date": datetime.datetime.strptime(
                extracted_metadata.publication_date, '%Y%m%d'
            ),
            "ojs_issue_number": extracted_metadata.ojs_issue_number,
            "ojs_type": extracted_metadata.ojs_type if extracted_metadata.ojs_type else "S",
            "city_of_buyer": [city_of_buyer for city_of_buyer in extracted_metadata.city_of_buyer],
            "name_of_buyer": [name_of_buyer for name_of_buyer in extracted_metadata.name_of_buyer],
            "original_language": self.get_map_value(mapping=languages_map, value=extracted_metadata.original_language),
            "country_of_buyer": self.get_map_value(mapping=countries_map, value=extracted_metadata.country_of_buyer),
            "eu_institution": False if extracted_metadata.eu_institution == '-' else True,
            "document_sent_date": datetime.datetime.strptime(
                extracted_metadata.document_sent_date, '%Y%m%d'
            ) if extracted_metadata.document_sent_date is not None else None,
            "deadline_for_submission": datetime.datetime.strptime(
                extracted_metadata.deadline_for_submission, '%Y%m%d'
            ) if extracted_metadata.deadline_for_submission is not None else None,
            "notice_type": self.get_map_value(mapping=notice_type_map, value=notice_type),
            "form_type": self.get_map_value(mapping=form_type_map, value=form_type),
            "place_of_performance": [self.get_map_value(mapping=nuts_map, value=place_of_performance.code) for
                                     place_of_performance
                                     in extracted_metadata.place_of_performance],
            "legal_basis_directive": self.get_map_value(mapping=legal_basis_map,
                                                        value=self.normalise_legal_basis_value(
                                                            extracted_metadata.legal_basis_directive)),
            "form_number": self.normalise_form_number(value=extracted_metadata.extracted_form_number)
        }

        return NormalisedMetadata(**metadata)
