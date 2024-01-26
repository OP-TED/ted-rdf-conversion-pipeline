import datetime
from typing import Tuple, List, Optional

import semantic_version

from ted_sws.core.model.metadata import NormalisedMetadata, NoticeSource
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.transform import MappingSuite
from ted_sws.data_manager.adapters.repository_abc import MappingSuiteRepositoryABC, NoticeRepositoryABC
from ted_sws.mapping_suite_processor.services.conceptual_mapping_generate_metadata import START_DATE_KEY, END_DATE_KEY, \
    MIN_XSD_VERSION_KEY, MAX_XSD_VERSION_KEY, E_FORMS_SUBTYPE_KEY, EFORMS_SDK_VERSIONS_KEY


def format_version_with_zero_patch(version_string:str) -> semantic_version.Version:
    """
    This will take a string version (1.7 or 1.7.6) and will transform it to a semantic version with 0 as patch
    1.7 -> 1.7.0
    1.7.6 -> 1.7.0
    """
    parsed_version = semantic_version.Version.coerce(version_string)
    return semantic_version.Version(major=parsed_version.major, minor=parsed_version.minor, patch=0)


def is_date_in_range(publication_date, constraint_start_date_value, constraint_end_date_value) -> bool:
    """
    This will return True or False if publication_date is in range looking at the start and end date constraints in the
    metadata of a mapping suite
    """
    if not constraint_start_date_value and not constraint_end_date_value:
        return True

    start_date = datetime.datetime.fromisoformat(constraint_start_date_value[0])
    end_date = datetime.datetime.fromisoformat(
        constraint_end_date_value[0] if constraint_end_date_value else datetime.datetime.now().isoformat())
    return start_date <= publication_date <= end_date


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

    if notice_metadata.notice_source == NoticeSource.ELECTRONIC_FORM:
        notice_xsd_version = notice_metadata.eform_sdk_version
        # eform sdk version value in metadata example: eforms-sdk-1.7 or  eforms-sdk-1.7.9
        # we need to extract only the version i.e 1.7 or 1.7.9
        eforms_sdk_version = notice_xsd_version.rsplit('-', 1)[1]
        constraint_version_range = [format_version_with_zero_patch(version) for version in
                                    constraints[EFORMS_SDK_VERSIONS_KEY]]
        in_version_range = format_version_with_zero_patch(eforms_sdk_version) in constraint_version_range
    else:
        notice_xsd_version = notice_metadata.xsd_version
        constraint_min_xsd_version = constraints[MIN_XSD_VERSION_KEY][0]
        constraint_max_xsd_version = constraints[MAX_XSD_VERSION_KEY][0]
        in_version_range = constraint_min_xsd_version <= notice_xsd_version <= constraint_max_xsd_version

    in_date_range = is_date_in_range(publication_date=notice_publication_date,
                                     constraint_start_date_value=constraints[START_DATE_KEY],
                                     constraint_end_date_value=constraints[END_DATE_KEY])
    eform_subtype_constraint_values = [str(eforms_subtype_value) for eforms_subtype_value in
                                       constraints[E_FORMS_SUBTYPE_KEY]]
    covered_eform_type = eform_subtype in eform_subtype_constraint_values

    return in_date_range and in_version_range and covered_eform_type


def notice_eligibility_checker(notice: Notice, mapping_suite_repository: MappingSuiteRepositoryABC) -> Tuple:
    """
    Check if notice is eligible for transformation
    :param notice:
    :param mapping_suite_repository:
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
