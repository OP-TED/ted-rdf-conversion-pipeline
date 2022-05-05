import datetime
from typing import Tuple

import pandas as pd

from ted_sws.core.model.metadata import NormalisedMetadata
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.transform import MappingSuite
from ted_sws.data_manager.adapters.repository_abc import MappingSuiteRepositoryABC, NoticeRepositoryABC
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

    constraint_start_date = datetime.datetime.strptime(constraints[START_DATE_KEY][0], "%Y-%m-%d")
    constraint_end_date = datetime.datetime.strptime(constraints[END_DATE_KEY][0], "%Y-%m-%d")
    constraint_min_xsd_version = constraints[MIN_XSD_VERSION_KEY][0]
    constraint_max_xsd_version = constraints[MAX_XSD_VERSION_KEY][0]

    in_date_range = constraint_start_date <= notice_publication_date <= constraint_end_date
    in_version_range = constraint_min_xsd_version <= notice_xsd_version <= constraint_max_xsd_version
    covered_eform_type = int(eform_subtype) in constraints[E_FORMS_SUBTYPE_KEY]

    return True if in_date_range and in_version_range and covered_eform_type else False


def transform_version_string_into_int(version_string: str) -> int:
    """
    Transforming a version string into a number. (example_version = "1.2.3")
    :param version_string:
    :return:
    """
    version_numbers = [int(x) for x in version_string.split(".")]
    assert len(version_numbers) == 3
    return ((version_numbers[0] * 100) + version_numbers[1]) * 100 + version_numbers[2]


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
        best_version = max([transform_version_string_into_int(version_string=mapping_suite.version) for mapping_suite in
                            possible_mapping_suites])
        mapping_suite_identifier = next((mapping_suite.identifier for mapping_suite in possible_mapping_suites if
                                         transform_version_string_into_int(
                                             version_string=mapping_suite.version) == best_version), None)
        notice.set_is_eligible_for_transformation(eligibility=True)
        return notice.ted_id, mapping_suite_identifier
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
