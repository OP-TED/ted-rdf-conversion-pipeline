from ted_sws.mapping_suite_processor.services.mapping_suite_digest_service import \
    replace_digest_api_address_for_mapping_suite


def test_replace_digest_api_address_for_mapping_suite(fake_mapping_suite):
    current_digest_api_address = "https://digest-api.ted-data.eu"
    new_digest_api_address = "https://new-digest-api.ted-data.eu"

    replace_digest_api_address_for_mapping_suite(fake_mapping_suite, current_digest_api_address, new_digest_api_address)
    for rml_mapping_rule in fake_mapping_suite.transformation_rule_set.rml_mapping_rules:
        assert current_digest_api_address not in rml_mapping_rule.file_content
        assert new_digest_api_address in rml_mapping_rule.file_content
