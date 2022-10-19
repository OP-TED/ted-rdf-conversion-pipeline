import datetime
from typing import Tuple

import semantic_version

from ted_sws.core.model.metadata import NormalisedMetadata
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.transform import MappingSuite
from ted_sws.data_manager.adapters.repository_abc import MappingSuiteRepositoryABC, NoticeRepositoryABC
from ted_sws.event_manager.services.log import log_notice_error
from ted_sws.mapping_suite_processor.services.conceptual_mapping_generate_metadata import START_DATE_KEY, END_DATE_KEY, \
    MIN_XSD_VERSION_KEY, MAX_XSD_VERSION_KEY, E_FORMS_SUBTYPE_KEY


def check_package(mapping_suite: MappingSuite, notice_metadata: NormalisedMetadata):
    """
    Check if mapping suite is valid for notice
    :param notice_metadata:
    :param mapping_suite:
    :return:
    """
    constraints = mapping_suite.metadata_constraints.constraints

    eform_subtype = notice_metadata.eforms_subtype
    notice_publication_date = datetime.datetime.fromisoformat(notice_metadata.publication_date)
    notice_xsd_version = notice_metadata.xsd_version

    end_date = constraints[END_DATE_KEY][0] if constraints[END_DATE_KEY] else datetime.datetime.now().isoformat()
    constraint_start_date = datetime.datetime.fromisoformat(constraints[START_DATE_KEY][0])
    constraint_end_date = datetime.datetime.fromisoformat(end_date)
    constraint_min_xsd_version = constraints[MIN_XSD_VERSION_KEY][0]
    constraint_max_xsd_version = constraints[MAX_XSD_VERSION_KEY][0]

    in_date_range = constraint_start_date <= notice_publication_date <= constraint_end_date
    in_version_range = constraint_min_xsd_version <= notice_xsd_version <= constraint_max_xsd_version
    covered_eform_type = int(eform_subtype) in constraints[E_FORMS_SUBTYPE_KEY]

    return True if in_date_range and in_version_range and covered_eform_type else False


def notice_eligibility_checker(notice: Notice, mapping_suite_repository: MappingSuiteRepositoryABC) -> Tuple:
    """
    Check if notice in eligible for transformation
    :param mapping_suite_repository:
    :param notice:
    :return:
    """

    possible_mapping_suites = []
    for mapping_suite in mapping_suite_repository.list():
        if check_package(mapping_suite=mapping_suite, notice_metadata=notice.normalised_metadata):
            possible_mapping_suites.append(mapping_suite)

    if possible_mapping_suites:
        best_version = possible_mapping_suites[0].version
        mapping_suite_identifier_with_version = possible_mapping_suites[0].get_mongodb_id()
        for mapping_suite in possible_mapping_suites[1:]:
            if semantic_version.Version(mapping_suite.version) > semantic_version.Version(best_version):
                best_version = mapping_suite.version
                mapping_suite_identifier_with_version = mapping_suite.get_mongodb_id()

        notice.set_is_eligible_for_transformation(eligibility=True)
        return notice.ted_id, mapping_suite_identifier_with_version
    else:
        notice.set_is_eligible_for_transformation(eligibility=False)
        log_notice_error(message=f"No MappingSuite was found for this notice form_number=[{notice.normalised_metadata.form_number}], eform_subtype=[{notice.normalised_metadata.eforms_subtype}], xsd_version=[{notice.normalised_metadata.xsd_version}]!",
                         notice_id=notice.ted_id)


def notice_eligibility_checker_by_id(notice_id: str, notice_repository: NoticeRepositoryABC,
                                     mapping_suite_repository: MappingSuiteRepositoryABC) -> Tuple:
    """
    Check if notice in eligible for transformation by giving a notice id
    :param notice_id:
    :param notice_repository:
    :param mapping_suite_repository:
    :return:
    """
    notice = notice_repository.get(reference=notice_id)
    if notice is None:
        raise ValueError(f'Notice, with {notice_id} id, was not found')
    result = notice_eligibility_checker(notice=notice, mapping_suite_repository=mapping_suite_repository)
    notice_repository.update(notice=notice)
    return result
