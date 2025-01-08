import pytest

from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.core.model.metadata import NormalisedMetadata
from ted_sws.core.model.notice import NoticeStatus, Notice
from ted_sws.notice_metadata_processor.adapters.notice_metadata_extractor import \
    DefaultNoticeMetadataExtractor, EformsNoticeMetadataExtractor
from ted_sws.notice_metadata_processor.adapters.notice_metadata_normaliser import \
    DefaultNoticeMetadataNormaliser, get_map_value, FORM_NUMBER_KEY, LEGAL_BASIS_KEY, SF_NOTICE_TYPE_KEY, \
    DOCUMENT_CODE_KEY, EformsNoticeMetadataNormaliser
from ted_sws.notice_metadata_processor.model.metadata import ExtractedMetadata
from ted_sws.notice_metadata_processor.services.metadata_constraints import filter_df_by_variables
from ted_sws.notice_metadata_processor.services.metadata_normalizer import normalise_notice, normalise_notice_by_id, \
    check_if_xml_manifestation_is_eform, find_metadata_extractor_based_on_xml_manifestation, \
    find_metadata_normaliser_based_on_xml_manifestation, extract_notice_metadata, normalise_notice_metadata, \
    extract_and_normalise_notice_metadata
from ted_sws.resources.mapping_files_registry import MappingFilesRegistry


def test_metadata_normaliser_by_notice(indexed_notice):
    notice = normalise_notice(indexed_notice)
    assert notice.normalised_metadata
    assert notice.normalised_metadata.title
    assert isinstance(notice.normalised_metadata.eforms_subtype, str)
    assert notice.status == NoticeStatus.NORMALISED_METADATA


def test_metadata_normaliser_by_notice_id(notice_id, notice_repository, notice_2020):
    notice_repository.add(notice_2020)
    notice = normalise_notice_by_id(notice_id=notice_2020.ted_id, notice_repository=notice_repository)
    assert notice.normalised_metadata
    assert notice.normalised_metadata.title
    assert notice.status == NoticeStatus.NORMALISED_METADATA


def test_metadata_normaliser_by_wrong_notice_id(notice_repository):
    notice_id = "wrong-notice-id"
    with pytest.raises(ValueError):
        normalise_notice_by_id(notice_id=notice_id, notice_repository=notice_repository)


def test_metadata_normaliser(indexed_notice):
    notice = indexed_notice
    normalise_notice(notice=notice)

    assert notice.normalised_metadata
    assert notice.normalised_metadata.title
    assert notice.status == NoticeStatus.NORMALISED_METADATA


def test_normalise_form_number(indexed_notice):
    default_notice_normaliser = DefaultNoticeMetadataNormaliser()
    assert default_notice_normaliser.normalise_form_number("FFFSA") == "FFFSA"
    assert default_notice_normaliser.normalise_form_number("F18") == "F18"
    assert default_notice_normaliser.normalise_form_number("F01") == "F01"
    assert default_notice_normaliser.normalise_form_number("F2") == "F02"
    assert default_notice_normaliser.normalise_form_number("22") == "F22"
    assert default_notice_normaliser.normalise_form_number("2") == "F02"
    assert default_notice_normaliser.normalise_form_number("F") == "F"
    assert default_notice_normaliser.normalise_form_number("TX01") == "TX01"
    assert default_notice_normaliser.normalise_form_number("TX1") == "TX01"
    assert default_notice_normaliser.normalise_form_number("FX03FG") == "FX03FG"
    assert default_notice_normaliser.normalise_form_number("1F03FG") == "1F03FG"


def test_normalise_legal_basis(indexed_notice):
    default_notice_normaliser = DefaultNoticeMetadataNormaliser()
    assert "32009L0081" == default_notice_normaliser.normalise_legal_basis_value(
        value="2009/81/EC")


def test_get_map_value():
    value = get_map_value(mapping=MappingFilesRegistry().countries, value="DE")
    assert value == "http://publications.europa.eu/resource/authority/country/DEU"


def test_filter_df_by_variables():
    df = MappingFilesRegistry().ef_notice_df
    filtered_df = filter_df_by_variables(df=df, form_type="planning",
                                         eform_notice_type="pin-only")

    assert len(filtered_df.index) == 5
    assert "32014L0024" in filtered_df["eform_legal_basis"].values


def test_get_form_type_and_notice_type():
    default_notice_metadata_normaliser = DefaultNoticeMetadataNormaliser()
    form_type, notice_type, legal_basis, eforms_subtype = default_notice_metadata_normaliser.get_form_type_and_notice_type(
        ef_map=MappingFilesRegistry().ef_notice_df,
        sf_map=MappingFilesRegistry().sf_notice_df,
        form_number="F02", extracted_notice_type=None,
        legal_basis="32014L0023", document_type_code="Y", filter_map=MappingFilesRegistry().filter_map_df)

    assert "competition" == form_type
    assert "cn-standard" == notice_type
    assert "32014L0024" == legal_basis
    assert "16" == eforms_subtype


def test_get_form_type_and_notice_type_F07():
    default_notice_metadata_normaliser = DefaultNoticeMetadataNormaliser()
    form_type, notice_type, legal_basis, eforms_subtype = default_notice_metadata_normaliser.get_form_type_and_notice_type(
        ef_map=MappingFilesRegistry().ef_notice_df,
        sf_map=MappingFilesRegistry().sf_notice_df,
        form_number="F07", extracted_notice_type=None,
        legal_basis="32014L0025", document_type_code="Y", filter_map=MappingFilesRegistry().filter_map_df)

    assert "competition" == form_type
    assert "qu-sy" == notice_type
    assert "32014L0025" == legal_basis
    assert "15.1" == eforms_subtype


def test_get_filter_values(indexed_notice):
    default_notice_metadata_normaliser = DefaultNoticeMetadataNormaliser()
    filter_map = MappingFilesRegistry().filter_map_df
    filter_variables_dict = default_notice_metadata_normaliser.get_filter_variables_values(form_number="F07",
                                                                                           filter_map=filter_map,
                                                                                           extracted_notice_type=None,
                                                                                           document_type_code="7",
                                                                                           legal_basis="legal")
    assert isinstance(filter_variables_dict, dict)
    assert filter_variables_dict[FORM_NUMBER_KEY] == "F07"
    assert filter_variables_dict[LEGAL_BASIS_KEY] is None
    assert filter_variables_dict[SF_NOTICE_TYPE_KEY] is None
    assert filter_variables_dict[DOCUMENT_CODE_KEY] is None

    with pytest.raises(Exception):
        default_notice_metadata_normaliser.get_filter_variables_values(form_number="F073",
                                                                       filter_map=filter_map,
                                                                       extracted_notice_type=None,
                                                                       document_type_code="7",
                                                                       legal_basis="legal")


def test_normalising_process_on_failed_notice_in_dag(notice_2021):
    extracted_metadata = DefaultNoticeMetadataExtractor(xml_manifestation=notice_2021.xml_manifestation)
    extracted_metadata_normaliser = DefaultNoticeMetadataNormaliser()
    filter_map = MappingFilesRegistry().filter_map_df
    filter_variables_dict = extracted_metadata_normaliser.get_filter_variables_values(
        form_number=extracted_metadata.extracted_form_number,
        filter_map=filter_map,
        extracted_notice_type=extracted_metadata.extracted_notice_type,
        document_type_code=extracted_metadata.extracted_document_type.code,
        legal_basis=extracted_metadata.legal_basis_directive)

    assert isinstance(filter_variables_dict, dict)
    assert filter_variables_dict[FORM_NUMBER_KEY] == "F21"
    assert filter_variables_dict[LEGAL_BASIS_KEY] is None
    assert filter_variables_dict[SF_NOTICE_TYPE_KEY] == "AWARD_CONTRACT"
    assert filter_variables_dict[DOCUMENT_CODE_KEY] is None

    form_type, notice_type, legal_basis, eforms_subtype = extracted_metadata_normaliser.get_form_type_and_notice_type(
        ef_map=MappingFilesRegistry().ef_notice_df,
        sf_map=MappingFilesRegistry().sf_notice_df,
        form_number=extracted_metadata.extracted_form_number,
        extracted_notice_type=extracted_metadata.extracted_notice_type,
        legal_basis=extracted_metadata.legal_basis_directive,
        document_type_code=extracted_metadata.extracted_document_type.code,
        filter_map=MappingFilesRegistry().filter_map_df)

    assert form_type == "result"
    assert notice_type == "can-social"
    assert legal_basis == "32014L0024"
    assert eforms_subtype == "33"


def test_check_if_xml_manifestation_is_eform(eform_notice_622690, notice_2018):
    is_eform_notice_622690_a_eform = check_if_xml_manifestation_is_eform(
        xml_manifestation=eform_notice_622690.xml_manifestation)
    is_notice_2018_a_eform = check_if_xml_manifestation_is_eform(xml_manifestation=notice_2018.xml_manifestation)

    assert is_eform_notice_622690_a_eform == True
    assert is_notice_2018_a_eform == False


def test_find_metadata_extractor_based_on_xml_manifestation(eform_notice_622690, notice_2018):
    assert isinstance(
        find_metadata_extractor_based_on_xml_manifestation(xml_manifestation=eform_notice_622690.xml_manifestation),
        EformsNoticeMetadataExtractor)
    assert isinstance(
        find_metadata_extractor_based_on_xml_manifestation(xml_manifestation=notice_2018.xml_manifestation),
        DefaultNoticeMetadataExtractor)


def test_find_metadata_normaliser_based_on_xml_manifestation(eform_notice_622690, notice_2018):
    assert isinstance(
        find_metadata_normaliser_based_on_xml_manifestation(xml_manifestation=eform_notice_622690.xml_manifestation),
        EformsNoticeMetadataNormaliser)
    assert isinstance(
        find_metadata_normaliser_based_on_xml_manifestation(xml_manifestation=notice_2018.xml_manifestation),
        DefaultNoticeMetadataNormaliser)


def test_extract_notice_metadata(eform_notice_622690, notice_2018):
    extractors = [EformsNoticeMetadataExtractor(xml_manifestation=eform_notice_622690.xml_manifestation),
                  DefaultNoticeMetadataExtractor(notice_2018.xml_manifestation)]
    for extractor in extractors:
        assert isinstance(extract_notice_metadata(metadata_extractor=extractor), ExtractedMetadata)


def test_normalise_notice_metadata(eform_notice_622690, notice_2018):
    extracted_metadata = extract_notice_metadata(
        metadata_extractor=EformsNoticeMetadataExtractor(xml_manifestation=eform_notice_622690.xml_manifestation))
    assert isinstance(normalise_notice_metadata(extracted_metadata=extracted_metadata,
                                                metadata_normaliser=EformsNoticeMetadataNormaliser()),
                      NormalisedMetadata)

    extracted_metadata = extract_notice_metadata(
        metadata_extractor=DefaultNoticeMetadataExtractor(xml_manifestation=notice_2018.xml_manifestation))
    assert isinstance(normalise_notice_metadata(extracted_metadata=extracted_metadata,
                                                metadata_normaliser=DefaultNoticeMetadataNormaliser()),
                      NormalisedMetadata)


def test_get_form_type_notice_type_and_legal_basis():
    form_type, notice_type, legal_basis = EformsNoticeMetadataNormaliser().get_form_type_notice_type_and_legal_basis(
        extracted_notice_subtype='20')
    assert form_type == 'competition'
    assert notice_type == 'cn-social'
    assert legal_basis == '32014L0024'


def test_normalising_notice_out_of_index(notice_normalisation_test_data_path):
    notice_xml_path = notice_normalisation_test_data_path / "2023-OJS153-00486429.xml"
    notice_content = notice_xml_path.read_text(encoding="utf-8")
    normalised_notice_metadata = extract_and_normalise_notice_metadata(
        xml_manifestation=XMLManifestation(object_data=notice_content))
    assert normalised_notice_metadata.eforms_subtype == "16"
    assert normalised_notice_metadata.notice_publication_number == "00486429-2023"

    broken_notice_xml_path = notice_normalisation_test_data_path / "no_eform_subtype_notice.xml"
    broke_notice_content = broken_notice_xml_path.read_text(encoding="utf-8")

    with pytest.raises(Exception):
        extract_and_normalise_notice_metadata(
            xml_manifestation=XMLManifestation(object_data=broke_notice_content))


def test_normalising_notice_with_spaces_in_notice_id(sample_indexed_ef_notice_with_spaces_in_publication_number: Notice,
                                                     sample_indexed_sf_notice_with_spaces_in_publication_number: Notice
                                                     ):
    normalised_ef_notice: Notice = normalise_notice(sample_indexed_ef_notice_with_spaces_in_publication_number)

    assert normalised_ef_notice.normalised_metadata.notice_publication_number.strip() == normalised_ef_notice.normalised_metadata.notice_publication_number

    normalised_sf_notice: Notice = normalise_notice(sample_indexed_sf_notice_with_spaces_in_publication_number)

    assert normalised_sf_notice.normalised_metadata.notice_publication_number.strip() == normalised_sf_notice.normalised_metadata.notice_publication_number