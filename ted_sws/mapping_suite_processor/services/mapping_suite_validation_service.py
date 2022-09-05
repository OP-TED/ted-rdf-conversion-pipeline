import pathlib

from ted_sws.mapping_suite_processor.adapters.mapping_suite_structure_checker import MappingSuiteStructureValidator


def validate_mapping_suite(mapping_suite_path: pathlib.Path) -> bool:
    mapping_suite_validator = MappingSuiteStructureValidator(mapping_suite_path)
    return mapping_suite_validator.is_valid()
