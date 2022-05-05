import json
import pathlib
from datetime import datetime
import pandas as pd

VERSION_FIELD = 'Mapping Version'
EPO_VERSION_FIELD = 'EPO version'
DESCRIPTION_FIELD = "Description"
TITLE_FIELD = 'Title'
IDENTIFIER_FIELD = 'Identifier'
E_FORMS_SUBTYPE_FIELD = "eForms Subtype"
START_DATE_FIELD = "Start Date"
END_DATE_FIELD = "End Date"
MIN_XSD_VERSION_FIELD = "Min XSD Version"
MAX_XSD_VERSION_FIELD = "Max XSD Version"

E_FORMS_SUBTYPE_KEY = "eforms_subtype"
START_DATE_KEY = "start_date"
END_DATE_KEY = "end_date"
MIN_XSD_VERSION_KEY = "min_xsd_version"
MAX_XSD_VERSION_KEY = "max_xsd_version"
TITLE_KEY = "title"
CREATED_KEY = "created_at"
IDENTIFIER_KEY = "identifier"
VERSION_KEY = "version"
DESCRIPTION_KEY = "description"
ONTOLOGY_VERSION_KEY = "ontology_version"
METADATA_CONSTRAINTS_KEY = "metadata_constraints"
CONSTRAINTS_KEY = "constraints"

CONCEPTUAL_MAPPINGS_METADATA_SHEET_NAME = "Metadata"


def generate_metadata(raw_metadata: dict) -> str:
    """
        This feature restructures the metadata into a default format.
        Metadata is formed from 2 parts: metadata for mapping suite and constraints on the mapping suite
    :param raw_metadata:
    :return:
    """

    def get_list_from_raw_metadata(field_key: str) -> list:
        data = raw_metadata[field_key][0]
        if pd.notna(data):
            return [x.strip() for x in str(data).split(',')]
        else:
            return []

    constraints = {E_FORMS_SUBTYPE_KEY: [int(x) for x in get_list_from_raw_metadata(E_FORMS_SUBTYPE_FIELD)],
                   START_DATE_KEY: get_list_from_raw_metadata(START_DATE_FIELD),
                   END_DATE_KEY: get_list_from_raw_metadata(END_DATE_FIELD),
                   MIN_XSD_VERSION_KEY: get_list_from_raw_metadata(MIN_XSD_VERSION_FIELD),
                   MAX_XSD_VERSION_KEY: get_list_from_raw_metadata(MAX_XSD_VERSION_FIELD)}

    metadata = {TITLE_KEY: raw_metadata[TITLE_FIELD][0], IDENTIFIER_KEY: raw_metadata[IDENTIFIER_FIELD][0],
                CREATED_KEY: datetime.now().isoformat(), VERSION_KEY: raw_metadata[VERSION_FIELD][0],
                ONTOLOGY_VERSION_KEY: raw_metadata[EPO_VERSION_FIELD][0],
                DESCRIPTION_KEY: raw_metadata[DESCRIPTION_FIELD][0],
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
