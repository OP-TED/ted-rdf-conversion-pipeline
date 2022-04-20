import json
import pathlib
from datetime import datetime
import pandas as pd

FORM_NUMBER_FIELD = 'Form number'
LEGAL_BASIS_FIELD = 'Legal Basis'
YEAR_FIELD = 'Year'
NOTICE_TYPE_FIELD = 'Notice type (eForms)'
FORM_TYPE_FIELD = 'Form type(eForms)'
VERSION_FIELD = 'Version'
EPO_VERSION_FIELD = 'EPO version'
XSD_VERSION_FIELD = 'XSD version number(s)'
TITLE_FIELD = 'Title'
IDENTIFIER_FIELD = 'Identifier'

FORM_NUMBER_KEY = "form_number"
LEGAL_BASIS_KEY = "legal_basis"
YEAR_KEY = "year"
NOTICE_TYPE_KEY = "notice_type"
FORM_TYPE_KEY = "form_type"
TITLE_KEY = "title"
CREATED_KEY = "created_at"
IDENTIFIER_KEY = "identifier"
VERSION_KEY = "version"
ONTOLOGY_VERSION_KEY = "ontology_version"
XSD_VERSION_KEY = "xsd_version"
METADATA_CONSTRAINTS_KEY = "metadata_constraints"
CONSTRAINTS_KEY = "constraints"

CONCEPTUAL_MAPPINGS_METADATA_SHEET_NAME = "Metadata"


def generate_metadata(raw_metadata: dict) -> str:
    """
        This feature restructures the metadata into a default format.
    :param raw_metadata:
    :return:
    """

    def get_list_from_raw_metadata(field_key: str) -> list:
        return [x.strip() for x in raw_metadata[field_key][0].split(',')]

    constraints = {FORM_NUMBER_KEY: get_list_from_raw_metadata(FORM_NUMBER_FIELD),
                   LEGAL_BASIS_KEY: get_list_from_raw_metadata(LEGAL_BASIS_FIELD),
                   YEAR_KEY: get_list_from_raw_metadata(YEAR_FIELD),
                   NOTICE_TYPE_KEY: get_list_from_raw_metadata(NOTICE_TYPE_FIELD),
                   FORM_TYPE_KEY: get_list_from_raw_metadata(FORM_TYPE_FIELD)}

    metadata = {TITLE_KEY: raw_metadata[TITLE_FIELD][0], IDENTIFIER_KEY: raw_metadata[IDENTIFIER_FIELD][0],
                CREATED_KEY: datetime.now().isoformat(), VERSION_KEY: raw_metadata[VERSION_FIELD][0],
                ONTOLOGY_VERSION_KEY: raw_metadata[EPO_VERSION_FIELD][0],
                XSD_VERSION_KEY: raw_metadata[XSD_VERSION_FIELD][0],
                METADATA_CONSTRAINTS_KEY: {CONSTRAINTS_KEY: constraints}}
    return json.dumps(metadata)


def mapping_suite_processor_generate_metadata(conceptual_mappings_file_path: pathlib.Path,
                                              output_metadata_file_path: pathlib.Path):
    """
        This function reads metadata from conceptual_mapping_file and generates metadata for a mapping suite package.
            The result is written to the output_metadata_file file.
    :param conceptual_mappings_file_path:
    :param output_metadata_file_path:
    :return:
    """
    with open(conceptual_mappings_file_path, 'rb') as excel_file:
        conceptual_mappings_metadata_df = pd.read_excel(excel_file, sheet_name=CONCEPTUAL_MAPPINGS_METADATA_SHEET_NAME)
        raw_metadata = conceptual_mappings_metadata_df.set_index('Field').T.to_dict('list')
        metadata = generate_metadata(raw_metadata=raw_metadata)

    with open(output_metadata_file_path, 'w') as metadata_file:
        metadata_file.write(metadata)
