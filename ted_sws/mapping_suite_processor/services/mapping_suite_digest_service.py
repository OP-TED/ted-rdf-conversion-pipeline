from ted_sws.core.model.transform import MappingSuite
from urllib.parse import urlparse


def replace_digest_api_address_for_mapping_suite(mapping_suite: MappingSuite, current_digest_api_address: str,
                                                 new_digest_api_address) -> MappingSuite:
    """
    Replace the digest API address

    Given a mapping suite (loaded into memory)
    AND the current digest API address
    AND the new digest API address
    When the replace operation is invoked
    Then the RML rules in the mapping suite no longer contain references to the CURRENT API address but to the NEW one.

    :param mapping_suite:
    :param current_digest_api_address:
    :param new_digest_api_address:
    :return:
    """

    urlparse(current_digest_api_address)
    urlparse(new_digest_api_address)

    rml_mapping_rules = mapping_suite.transformation_rule_set.rml_mapping_rules
    for rml_mapping_rule in rml_mapping_rules:
        rml_mapping_rule_content = rml_mapping_rule.file_content
        rml_mapping_rule.file_content = rml_mapping_rule_content.replace(current_digest_api_address,
                                                                         new_digest_api_address)

    return mapping_suite

