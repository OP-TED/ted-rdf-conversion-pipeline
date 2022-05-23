from ted_sws.resources.mapping_files_registry import MappingFilesRegistry

FORM_NUMBER_COLUMN_NAME = "form_number"
EFORMS_SUBTYPE_COLUMN_NAME = "eforms_subtype"

def test_dummy():
    sf_notice_df = MappingFilesRegistry().sf_notice_df
    form_numbers = list(set(sf_notice_df[FORM_NUMBER_COLUMN_NAME].values.tolist()))
    eforms_subtypes = list(set(sf_notice_df[EFORMS_SUBTYPE_COLUMN_NAME].values.tolist()))
    print(form_numbers)
    print(eforms_subtypes)