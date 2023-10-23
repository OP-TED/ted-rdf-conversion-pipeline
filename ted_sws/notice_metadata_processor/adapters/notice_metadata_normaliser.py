import abc
from datetime import datetime
from typing import Dict, Tuple, List
import re
import pandas as pd

from ted_sws.core.model.metadata import NormalisedMetadata, LanguageTaggedString
from ted_sws.notice_metadata_processor.model.metadata import ExtractedMetadata
from ted_sws.notice_metadata_processor.services.metadata_constraints import filter_df_by_variables
from ted_sws.resources.mapping_files_registry import MappingFilesRegistry

JOIN_SEP = " :: "
E_FORMS_SUBTYPE_KEY = "eforms_subtype"
E_FORM_NOTICE_TYPE_COLUMN = "eform_notice_type"
E_FORM_LEGAL_BASIS_COLUMN = "eform_legal_basis"
FORM_NUMBER_KEY = "form_number"
FORM_TYPE_KEY = "form_type"
SF_NOTICE_TYPE_KEY = "sf_notice_type"
DOCUMENT_CODE_KEY = "document_code"
LEGAL_BASIS_KEY = "legal_basis"
LEGAL_BASIS_DIRECTIVE_KEY = "legal_basis_directive"
EXTRACTED_LEGAL_BASIS_KEY = "extracted_legal_basis_directive"
PLACE_OF_PERFORMANCE_KEY = "place_of_performance"
TITLE_KEY = "title"
LONG_TITLE_KEY = "long_title"
NOTICE_NUMBER_KEY = "notice_publication_number"
PUBLICATION_DATE_KEY = "publication_date"
OJS_NUMBER_KEY = "ojs_issue_number"
OJS_TYPE_KEY = "ojs_type"
BUYER_CITY_KEY = "city_of_buyer"
BUYER_NAME_KEY = "name_of_buyer"
LANGUAGE_KEY = "original_language"
BUYER_COUNTRY_KEY = "country_of_buyer"
EU_INSTITUTION_KEY = "eu_institution"
SENT_DATE_KEY = "document_sent_date"
DEADLINE_DATE_KEY = "deadline_for_submission"
NOTICE_TYPE_KEY = "notice_type"
XSD_VERSION_KEY = "xsd_version"
ENGLISH_LANGUAGE_TAG = "EN"
mapping_registry = MappingFilesRegistry()


def get_map_list_value_by_code(mapping: Dict, listing: List):
    result = []
    for element in listing:
        if element:
            map_value = get_map_value(mapping=mapping, value=element.code)
            if map_value:
                result.append(map_value)
    return result


def get_map_value(mapping: Dict, value: str) -> str:
    """
    Returns mapped URI for value
    :param mapping:
    :param value:
    :return:
    """
    entry_list = [element for element in mapping['results']['bindings'] if
                  element['code']['value'] == value.strip()]
    entry = None
    if entry_list:
        entry = entry_list[0]

    return entry['conceptURI']['value'] if entry else None


class NoticeMetadataNormaliserABC(abc.ABC):
    """
     Metadata normaliser for standard forms
    """

    @abc.abstractmethod
    def normalise_metadata(self, extracted_metadata: ExtractedMetadata) -> NormalisedMetadata:
        """
            Normalise metadata
        """


class DefaultNoticeMetadataNormaliser(NoticeMetadataNormaliserABC):

    @classmethod
    def normalise_legal_basis_value(cls, value: str) -> str:
        """
        Transforms and returns Legal Basis value
        :param value:
        :return:
        """
        pattern = "3{year}L{number}"
        normalised_value = value
        parts = value.split("/") if value and ("/" in value) else [value]
        if len(parts) > 1:
            normalised_value = pattern.format(year=parts[0], number=parts[1].rjust(4, "0"))

        return normalised_value

    @classmethod
    def normalise_form_number(cls, value: str) -> str:
        """
        Normalise form number to be F{number} format.
        ##Decided to keep normalisation of the input data
            Rules:
            * The form number should start with a letter ("F", "T")
            * The form number isn't always a number (CEI,EEIG)
            * If the number is between 1 - 9 then it must have 0 as prefix (F02 not F2)
        :param value:
        :return:
        """
        if value:
            form_number_parts = re.split(r"(?=\d)", value, 1)
            if len(form_number_parts) == 2:
                text_part: str = form_number_parts[0] if form_number_parts[0] else "F"
                number_part: str = form_number_parts[1]
                if text_part.isalpha() and number_part.isdecimal():
                    number_part = "0" + number_part if number_part and len(number_part) < 2 else number_part
                    return text_part + number_part
        return value

    @classmethod
    def get_filter_variables_values(cls, form_number: str, extracted_notice_type: str, legal_basis: str,
                                    document_type_code: str, filter_map: pd.DataFrame) -> dict:
        """
        Get necessary values to filter mapping dataframe
        :param form_number:
        :param extracted_notice_type:
        :param legal_basis:
        :param document_type_code:
        :param filter_map:
        :return:
        """
        variables = {
            FORM_NUMBER_KEY: form_number,
            SF_NOTICE_TYPE_KEY: extracted_notice_type,
            DOCUMENT_CODE_KEY: document_type_code,
            LEGAL_BASIS_KEY: legal_basis
        }
        try:
            filter_variables = \
                filter_map.query(f"{FORM_NUMBER_KEY}=='{variables[FORM_NUMBER_KEY]}'").to_dict(orient='records')[0]
        except:
            raise Exception(
                f"This notice doesn't have a form number or the extracted form number is not in the mapping. "
                f"Form number found is {form_number}, document code is {document_type_code} and legal basis is {legal_basis}")

        for key, value in filter_variables.items():
            if value == 0:
                filter_variables[key] = None
            if value == 1:
                filter_variables[key] = variables[key]

        return filter_variables

    @classmethod
    def get_form_type_and_notice_type(cls, filter_map: pd.DataFrame, ef_map: pd.DataFrame, sf_map: pd.DataFrame,
                                      form_number: str,
                                      extracted_notice_type: str, legal_basis: str, document_type_code: str) -> Tuple:
        """
        Returns notice_type and form_type
        :param ef_map:
        :param filter_map:
        :param sf_map:
        :param form_number:
        :param extracted_notice_type:
        :param legal_basis:
        :param document_type_code:
        :return:
        """
        mapping_df = pd.merge(sf_map, ef_map, on=E_FORMS_SUBTYPE_KEY, how="left")
        filter_variables = cls.get_filter_variables_values(form_number=form_number, filter_map=filter_map,
                                                           extracted_notice_type=extracted_notice_type,
                                                           legal_basis=legal_basis,
                                                           document_type_code=document_type_code)
        filtered_df = filter_df_by_variables(df=mapping_df, form_number=filter_variables[FORM_NUMBER_KEY],
                                             sf_notice_type=filter_variables[SF_NOTICE_TYPE_KEY],
                                             legal_basis=filter_variables[LEGAL_BASIS_KEY],
                                             document_code=filter_variables[DOCUMENT_CODE_KEY])
        try:
            form_type = filtered_df[FORM_TYPE_KEY].values[0]
            notice_type = filtered_df[E_FORM_NOTICE_TYPE_COLUMN].values[0]
            legal_basis = filtered_df[E_FORM_LEGAL_BASIS_COLUMN].values[0]
            eforms_subtype = filtered_df[E_FORMS_SUBTYPE_KEY].values[0]
        except:
            raise Exception(
                f"This notice can't be mapped with the current mapping files (standard forms mapping and eforms mapping)."
                f"Searched values: form number={form_number}, extracted_notice_type {extracted_notice_type},"
                f" legal_basis {legal_basis}, document_code {document_type_code}. "
                f"Therefore form_type, notice_type, legal_basis and eforms_subtype fields can't be normalised")

        return form_type, notice_type, legal_basis, eforms_subtype

    @classmethod
    def iso_date_format(cls, _date: str, with_none=False):
        if _date or not with_none:
            return datetime.strptime(_date, '%Y%m%d').isoformat()
        return None

    def normalise_metadata(self, extracted_metadata: ExtractedMetadata) -> NormalisedMetadata:
        """
            Generate the normalised metadata
        :return:
        """
        countries_map = mapping_registry.countries
        form_type_map = mapping_registry.form_type
        languages_map = mapping_registry.languages
        legal_basis_map = mapping_registry.legal_basis
        notice_type_map = mapping_registry.notice_type
        nuts_map = mapping_registry.nuts
        standard_forms_map = mapping_registry.sf_notice_df
        eforms_map = mapping_registry.ef_notice_df
        filter_map = mapping_registry.filter_map_df
        form_type, notice_type, legal_basis, eforms_subtype = self.get_form_type_and_notice_type(
            sf_map=standard_forms_map, ef_map=eforms_map, filter_map=filter_map,
            extracted_notice_type=extracted_metadata.extracted_notice_type,
            form_number=self.normalise_form_number(
                extracted_metadata.extracted_form_number),
            legal_basis=self.normalise_legal_basis_value(
                extracted_metadata.legal_basis_directive),
            document_type_code=extracted_metadata.extracted_document_type.code
        )
        extracted_metadata = extracted_metadata

        metadata = {
            TITLE_KEY: [title.title for title in extracted_metadata.title],
            LONG_TITLE_KEY: [
                LanguageTaggedString(text=JOIN_SEP.join(
                    [
                        title.title_country.text,
                        title.title_city.text,
                        title.title.text
                    ]),
                    language=title.title.language) for title in extracted_metadata.title
            ],
            NOTICE_NUMBER_KEY: extracted_metadata.notice_publication_number,
            PUBLICATION_DATE_KEY: self.iso_date_format(extracted_metadata.publication_date),
            OJS_NUMBER_KEY: extracted_metadata.ojs_issue_number,
            OJS_TYPE_KEY: extracted_metadata.ojs_type if extracted_metadata.ojs_type else "S",
            BUYER_CITY_KEY: [city_of_buyer for city_of_buyer in extracted_metadata.city_of_buyer],
            BUYER_NAME_KEY: [name_of_buyer for name_of_buyer in extracted_metadata.name_of_buyer],
            LANGUAGE_KEY: get_map_value(mapping=languages_map, value=extracted_metadata.original_language),
            BUYER_COUNTRY_KEY: get_map_value(mapping=countries_map, value=extracted_metadata.country_of_buyer),
            EU_INSTITUTION_KEY: False if extracted_metadata.eu_institution == '-' else True,
            SENT_DATE_KEY: self.iso_date_format(extracted_metadata.document_sent_date, True),
            DEADLINE_DATE_KEY: self.iso_date_format(extracted_metadata.deadline_for_submission, True),
            NOTICE_TYPE_KEY: get_map_value(mapping=notice_type_map, value=notice_type),
            FORM_TYPE_KEY: get_map_value(mapping=form_type_map, value=form_type),
            PLACE_OF_PERFORMANCE_KEY: get_map_list_value_by_code(
                mapping=nuts_map,
                listing=extracted_metadata.place_of_performance
            ),
            EXTRACTED_LEGAL_BASIS_KEY: get_map_value(mapping=legal_basis_map,
                                                     value=self.normalise_legal_basis_value(
                                                         extracted_metadata.legal_basis_directive
                                                     )) if extracted_metadata.legal_basis_directive else None,
            FORM_NUMBER_KEY: self.normalise_form_number(value=extracted_metadata.extracted_form_number),
            LEGAL_BASIS_DIRECTIVE_KEY: get_map_value(mapping=legal_basis_map, value=legal_basis),
            E_FORMS_SUBTYPE_KEY: str(eforms_subtype),
            XSD_VERSION_KEY: extracted_metadata.xml_schema_version
        }

        return NormalisedMetadata(**metadata)


class EformsNoticeMetadataNormaliser(NoticeMetadataNormaliserABC):
    """
     Metadata normaliser for eForms
    """

    @classmethod
    def iso_date_format(cls, _date: str, with_none=False):
        if _date or not with_none:
            if 'Z' in _date:
                # Replace 'Z' with '+00:00' and parse
                _date = _date.replace('Z', '+00:00')
            return datetime.fromisoformat(_date).isoformat()
        return None

    @classmethod
    def get_form_type_notice_type_and_legal_basis(cls, extracted_notice_subtype: str) -> Tuple:
        """
         Get the values for form type, notice type and legal basis from the eForm mapping files
        """
        ef_map: pd.DataFrame = mapping_registry.ef_notice_df
        filtered_df = ef_map.query(f"{E_FORMS_SUBTYPE_KEY}=='{extracted_notice_subtype}'").to_dict(orient='records')[0]
        try:
            form_type = filtered_df[FORM_TYPE_KEY]
            notice_type = filtered_df[E_FORM_NOTICE_TYPE_COLUMN]
            legal_basis = filtered_df[E_FORM_LEGAL_BASIS_COLUMN]
        except:
            raise Exception(
                f"This notice can't be mapped with the current mapping files (standard forms mapping and eforms mapping)."
                f"Searched values: notice_subtype = {extracted_notice_subtype},"
                f"Therefore form_type, notice_type, legal_basis and eforms_subtype fields can't be normalised")

        return form_type, notice_type, legal_basis

    def normalise_metadata(self, extracted_metadata: ExtractedMetadata) -> NormalisedMetadata:
        """
            Generate the normalised metadata
        :return:
        """
        extracted_metadata = extracted_metadata
        form_type_map = mapping_registry.form_type
        languages_map = mapping_registry.languages
        legal_basis_map = mapping_registry.legal_basis
        notice_type_map = mapping_registry.notice_type
        nuts_map = mapping_registry.nuts
        form_type, notice_type, legal_basis = self.get_form_type_notice_type_and_legal_basis(
            extracted_notice_subtype=extracted_metadata.extracted_notice_subtype)
        metadata = {
            TITLE_KEY: [title.title for title in extracted_metadata.title],
            LONG_TITLE_KEY: [
                LanguageTaggedString(text=JOIN_SEP.join(
                    [
                        title.title_country.text,
                        title.title.text
                    ]),
                    language=title.title.language) for title in extracted_metadata.title
            ],
            NOTICE_NUMBER_KEY: extracted_metadata.notice_publication_number,
            PUBLICATION_DATE_KEY: self.iso_date_format(extracted_metadata.publication_date),
            OJS_NUMBER_KEY: extracted_metadata.ojs_issue_number,
            OJS_TYPE_KEY: extracted_metadata.ojs_type if extracted_metadata.ojs_type else "S",
            LANGUAGE_KEY: get_map_value(mapping=languages_map, value=extracted_metadata.original_language),
            SENT_DATE_KEY: self.iso_date_format(extracted_metadata.document_sent_date, True),
            DEADLINE_DATE_KEY: self.iso_date_format(extracted_metadata.deadline_for_submission, True),
            NOTICE_TYPE_KEY: get_map_value(mapping=notice_type_map, value=notice_type),
            FORM_TYPE_KEY: get_map_value(mapping=form_type_map, value=form_type),
            PLACE_OF_PERFORMANCE_KEY: get_map_list_value_by_code(
                mapping=nuts_map,
                listing=extracted_metadata.place_of_performance
            ),
            EXTRACTED_LEGAL_BASIS_KEY: get_map_value(mapping=legal_basis_map,
                                                     value=extracted_metadata.legal_basis_directive
                                                     ) if extracted_metadata.legal_basis_directive else None,
            FORM_NUMBER_KEY: '',
            LEGAL_BASIS_DIRECTIVE_KEY: get_map_value(mapping=legal_basis_map,
                                                     value=legal_basis),
            E_FORMS_SUBTYPE_KEY: extracted_metadata.extracted_notice_subtype,
            XSD_VERSION_KEY: extracted_metadata.xml_schema_version
        }

        return NormalisedMetadata(**metadata)
