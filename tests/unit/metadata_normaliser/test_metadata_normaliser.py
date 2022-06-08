import pytest

from ted_sws.core.model.notice import NoticeStatus
from ted_sws.core.service.metadata_constraints import filter_df_by_variables
from ted_sws.resources.mapping_files_registry import MappingFilesRegistry
from ted_sws.metadata_normaliser.services.metadata_normalizer import normalise_notice, normalise_notice_by_id, \
    MetadataNormaliser, ExtractedMetadataNormaliser, FORM_NUMBER_KEY, SF_NOTICE_TYPE_KEY, LEGAL_BASIS_KEY, \
    DOCUMENT_CODE_KEY
from ted_sws.metadata_normaliser.services.xml_manifestation_metadata_extractor import XMLManifestationMetadataExtractor


def test_metadata_normaliser_by_notice(raw_notice):
    notice = normalise_notice(raw_notice)
    assert notice.normalised_metadata
    assert notice.normalised_metadata.title
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


def test_metadata_normaliser(raw_notice):
    notice = raw_notice
    MetadataNormaliser(notice=notice).normalise_metadata()

    assert notice.normalised_metadata
    assert notice.normalised_metadata.title
    assert notice.status == NoticeStatus.NORMALISED_METADATA


def test_normalise_form_number(raw_notice):
    extracted_metadata = XMLManifestationMetadataExtractor(xml_manifestation=raw_notice.xml_manifestation).to_metadata()
    extracted_metadata_normaliser = ExtractedMetadataNormaliser(extracted_metadata=extracted_metadata)
    assert "18" == extracted_metadata.extracted_form_number
    assert "F18" == extracted_metadata_normaliser.normalise_form_number(value=extracted_metadata.extracted_form_number)


def test_normalise_legal_basis(raw_notice):
    extracted_metadata = XMLManifestationMetadataExtractor(xml_manifestation=raw_notice.xml_manifestation).to_metadata()
    extracted_metadata_normaliser = ExtractedMetadataNormaliser(extracted_metadata=extracted_metadata)
    assert "2009/81/EC" == extracted_metadata.legal_basis_directive
    assert "32009L0081" == extracted_metadata_normaliser.normalise_legal_basis_value(
        value=extracted_metadata.legal_basis_directive)


def test_get_map_value(raw_notice):
    extracted_metadata = XMLManifestationMetadataExtractor(xml_manifestation=raw_notice.xml_manifestation).to_metadata()
    extracted_metadata_normaliser = ExtractedMetadataNormaliser(extracted_metadata=extracted_metadata)
    value = extracted_metadata_normaliser.get_map_value(mapping=MappingFilesRegistry().countries, value="DE")
    assert value == "http://publications.europa.eu/resource/authority/country/DEU"


def test_filter_df_by_variables():
    df = MappingFilesRegistry().ef_notice_df
    filtered_df = filter_df_by_variables(df=df, form_type="planning",
                                         eform_notice_type="pin-only")

    assert len(filtered_df.index) == 3
    assert "32014L0024" in filtered_df["eform_legal_basis"].values


def test_get_form_type_and_notice_type(raw_notice):
    extracted_metadata = XMLManifestationMetadataExtractor(xml_manifestation=raw_notice.xml_manifestation).to_metadata()
    extracted_metadata_normaliser = ExtractedMetadataNormaliser(extracted_metadata=extracted_metadata)
    form_type, notice_type, legal_basis, eforms_subtype = extracted_metadata_normaliser.get_form_type_and_notice_type(
        ef_map=MappingFilesRegistry().ef_notice_df,
        sf_map=MappingFilesRegistry().sf_notice_df,
        form_number="F02", extracted_notice_type=None,
        legal_basis="32014L0023", document_type_code="Y", filter_map=MappingFilesRegistry().filter_map_df)

    assert "competition" == form_type
    assert "cn-standard" == notice_type
    assert "32014L0024" == legal_basis
    assert "16" == eforms_subtype


def test_get_filter_values(raw_notice):
    extracted_metadata = XMLManifestationMetadataExtractor(xml_manifestation=raw_notice.xml_manifestation).to_metadata()
    extracted_metadata_normaliser = ExtractedMetadataNormaliser(extracted_metadata=extracted_metadata)
    filter_map = MappingFilesRegistry().filter_map_df
    filter_variables_dict = extracted_metadata_normaliser.get_filter_variables_values(form_number="F07",
                                                                                      filter_map=filter_map,
                                                                                      extracted_notice_type=None,
                                                                                      document_type_code="7",
                                                                                      legal_basis="legal")
    assert isinstance(filter_variables_dict,dict)
    assert filter_variables_dict[FORM_NUMBER_KEY] == "F07"
    assert filter_variables_dict[LEGAL_BASIS_KEY] is None
    assert filter_variables_dict[SF_NOTICE_TYPE_KEY] is None
    assert filter_variables_dict[DOCUMENT_CODE_KEY] is None

    with pytest.raises(Exception):
        extracted_metadata_normaliser.get_filter_variables_values(form_number="F073",
                                                                  filter_map=filter_map,
                                                                  extracted_notice_type=None,
                                                                  document_type_code="7",
                                                                  legal_basis="legal")

def test_normalising_process_on_failed_notice_in_dag(notice_2021):
    extracted_metadata = XMLManifestationMetadataExtractor(
        xml_manifestation=notice_2021.xml_manifestation).to_metadata()
    extracted_metadata_normaliser = ExtractedMetadataNormaliser(extracted_metadata=extracted_metadata)
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
