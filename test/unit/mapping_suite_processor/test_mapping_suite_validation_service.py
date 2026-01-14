from src.ted_sws.mapping_suite_processor.services.mapping_suite_validation_service import validate_mapping_package


def test_validate_mapping_package(mapping_package):
    assert validate_mapping_package(mapping_package)


def test_validate_eforms_mapping_package(eforms_mapping_package):
    assert validate_mapping_package(eforms_mapping_package)
