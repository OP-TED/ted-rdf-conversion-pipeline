import pathlib

from ted_sws.mapping_suite_processor.adapters.mapping_suite_structure_checker import MappingSuiteStructureValidator


def validate_mapping_suite(mapping_suite_path: pathlib.Path):

    mapping_suite_path = MappingSuiteStructureValidator(mapping_suite_path)
    mapping_suite_path.validate_core_structure()
    mapping_suite_path.validate_expanded_structure()
    mapping_suite_path.validate_output_structure()
    mapping_suite_path.check_metadata_consistency()
    return True
