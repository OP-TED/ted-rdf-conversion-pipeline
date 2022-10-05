import json
import pathlib
from datetime import datetime

import pandas as pd

from ted_sws.data_manager.adapters.mapping_suite_repository import MS_TRANSFORM_FOLDER_NAME, MS_METADATA_FILE_NAME, \
    MS_CONCEPTUAL_MAPPING_FILE_NAME
from ted_sws.mapping_suite_processor.adapters.mapping_suite_hasher import MappingSuiteHasher
from ted_sws.mapping_suite_processor.services.conceptual_mapping_reader import IDENTIFIER_FIELD, TITLE_FIELD, \
    DESCRIPTION_FIELD, VERSION_FIELD, EPO_VERSION_FIELD, E_FORMS_SUBTYPE_FIELD, START_DATE_FIELD, END_DATE_FIELD, \
    MIN_XSD_VERSION_FIELD, MAX_XSD_VERSION_FIELD
from ted_sws.mapping_suite_processor.services.conceptual_mapping_reader import mapping_suite_read_metadata

# This set of constants refers to keys in metadata.json corresponding to the fields Conceptual Mapping file
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
MAPPING_SUITE_HASH = "mapping_suite_hash_digest"


def generate_metadata(raw_metadata: dict) -> dict:
    """
        This feature restructures the metadata into a default format.
        Metadata is formed from 2 parts: metadata for mapping suite and constraints on the mapping suite
    :param raw_metadata:
    :return:
    """

    def get_list_from_raw_metadata(raw_metadata: dict, field_key: str) -> list:
        data = raw_metadata[field_key][0]
        if pd.notna(data):
            return [x.strip() for x in str(data).split(',')]
        else:
            return []

    constraints = {
        E_FORMS_SUBTYPE_KEY: [int(float(x)) for x in get_list_from_raw_metadata(raw_metadata, E_FORMS_SUBTYPE_FIELD)],
        START_DATE_KEY: get_list_from_raw_metadata(raw_metadata, START_DATE_FIELD),
        END_DATE_KEY: get_list_from_raw_metadata(raw_metadata, END_DATE_FIELD),
        MIN_XSD_VERSION_KEY: get_list_from_raw_metadata(raw_metadata, MIN_XSD_VERSION_FIELD),
        MAX_XSD_VERSION_KEY: get_list_from_raw_metadata(raw_metadata, MAX_XSD_VERSION_FIELD)}

    metadata = {TITLE_KEY: raw_metadata[TITLE_FIELD][0], IDENTIFIER_KEY: raw_metadata[IDENTIFIER_FIELD][0],
                CREATED_KEY: datetime.now().isoformat(), VERSION_KEY: raw_metadata[VERSION_FIELD][0],
                ONTOLOGY_VERSION_KEY: raw_metadata[EPO_VERSION_FIELD][0],
                DESCRIPTION_KEY: raw_metadata[DESCRIPTION_FIELD][0],
                METADATA_CONSTRAINTS_KEY: {CONSTRAINTS_KEY: constraints},
                }
    return metadata


def mapping_suite_processor_generate_metadata(mapping_suite_path: pathlib.Path,
                                              output_metadata_file_path: pathlib.Path = None,
                                              conceptual_mappings_file_path: pathlib.Path = None):
    """
        This function reads metadata from conceptual_mapping_file and generates metadata for a mapping suite package.
            The result is written to the output_metadata_file file.
    :param mapping_suite_path:
    :param output_metadata_file_path:
    :param conceptual_mappings_file_path:
    :return:
    """

    if output_metadata_file_path is None:
        output_metadata_file_path = mapping_suite_path / MS_METADATA_FILE_NAME

    if conceptual_mappings_file_path is None:
        conceptual_mappings_file_path = mapping_suite_path / MS_TRANSFORM_FOLDER_NAME / MS_CONCEPTUAL_MAPPING_FILE_NAME

    metadata = {}
    raw_metadata = mapping_suite_read_metadata(conceptual_mappings_file_path)
    conceptual_mapping_metadata = generate_metadata(raw_metadata=raw_metadata)
    metadata.update(conceptual_mapping_metadata)

    hashing_metadata = {MAPPING_SUITE_HASH: MappingSuiteHasher(mapping_suite_path).hash_mapping_suite(
        with_version=metadata[VERSION_KEY]
    )}
    metadata.update(hashing_metadata)

    with open(output_metadata_file_path, 'w') as metadata_file:
        metadata_file.write(json.dumps(metadata, indent=2))
