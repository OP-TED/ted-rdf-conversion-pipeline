from ted_sws.mapping_suite_processor.services.mapping_suite_validation_service import validate_mapping_suite


def test_validate_mapping_suite(mapping_suite):
    assert validate_mapping_suite(mapping_suite)


def test_validate_eforms_mapping_suite(eforms_mapping_suite):
    assert validate_mapping_suite(eforms_mapping_suite)
