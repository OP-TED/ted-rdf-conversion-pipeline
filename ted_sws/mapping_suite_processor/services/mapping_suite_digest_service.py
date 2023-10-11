from urllib.parse import urlparse

from ted_sws import config
from ted_sws.core.model.transform import MappingSuite


def update_digest_api_address_for_mapping_suite(mapping_suite: MappingSuite,
                                                current_digest_api_address: str = None,
                                                new_digest_api_address: str = None,
                                                ) -> MappingSuite:
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
    if current_digest_api_address is None:
        current_digest_api_address = config.ID_MANAGER_DEV_API_HOST
    if new_digest_api_address is None:
        new_digest_api_address = config.ID_MANAGER_PROD_API_HOST

    if not new_digest_api_address or not current_digest_api_address \
            or new_digest_api_address == current_digest_api_address:
        return mapping_suite

    urlparse(current_digest_api_address)
    urlparse(new_digest_api_address)

    if mapping_suite.transformation_rule_set and mapping_suite.transformation_rule_set.rml_mapping_rules:
        rml_mapping_rules = mapping_suite.transformation_rule_set.rml_mapping_rules
        for rml_mapping_rule in rml_mapping_rules:
            rml_mapping_rule_content = rml_mapping_rule.file_content
            if rml_mapping_rule_content:
                rml_mapping_rule.file_content = rml_mapping_rule_content.replace(current_digest_api_address,
                                                                                 new_digest_api_address)

    return mapping_suite
