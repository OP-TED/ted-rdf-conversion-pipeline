from pathlib import Path
from typing import Dict, Union

from ted_sws.core.model.transform import ConceptualMapping
from ted_sws.mapping_suite_processor.adapters.conceptual_mapping_reader import ConceptualMappingReader


def conceptual_mapping_read_list_from_pd_value(value):
    return ConceptualMappingReader.read_list_from_pd_value(value)


def mapping_suite_read_metadata(conceptual_mappings_file_path: Path) -> Dict:
    return ConceptualMappingReader.mapping_suite_read_metadata(conceptual_mappings_file_path)


def mapping_suite_read_conceptual_mapping(conceptual_mappings_file_path: Path) -> \
        Union[ConceptualMapping, None]:
    return ConceptualMappingReader.mapping_suite_read_conceptual_mapping(conceptual_mappings_file_path)
