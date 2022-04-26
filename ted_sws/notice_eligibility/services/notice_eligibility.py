from datetime import datetime
from typing import Tuple

import pandas as pd

from ted_sws.core.model.metadata import NormalisedMetadata
from ted_sws.core.model.notice import Notice
from ted_sws.core.model.transform import MetadataConstraints, MappingSuite
from ted_sws.core.service.metadata_constraints import filter_df_by_variables
from ted_sws.data_manager.adapters.repository_abc import MappingSuiteRepositoryABC, NoticeRepositoryABC


def create_eligibility_df(metadata_constraint: MetadataConstraints) -> pd.DataFrame:
    """
     Create a dataframe with all possible combinations from constraints
    :param metadata_constraint:
    :return:
    """
    filtered_constraints = {key: value for key, value in metadata_constraint.constraints.items() if value}
    data_list = [filtered_constraints[key] for key in filtered_constraints.keys()]
    index = pd.MultiIndex.from_product(data_list, names=filtered_constraints.keys())
    return pd.DataFrame(index=index).reset_index()


def check_package(mapping_suite: MappingSuite, notice_metadata: NormalisedMetadata):
    """
    Check if mapping suite is valid for notice
    :param notice_metadata:
    :param mapping_suite:
    :return:
    """
    checking_df = create_eligibility_df(metadata_constraint=mapping_suite.metadata_constraints)
    legal_basis = notice_metadata.legal_basis_directive.split("/")[-1]
    year = str(datetime.fromisoformat(notice_metadata.publication_date).year)
    form_number = notice_metadata.form_number
    filtered_df = filter_df_by_variables(df=checking_df, form_number=form_number, legal_basis=legal_basis, year=year)
    return True if not filtered_df.empty else False


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
