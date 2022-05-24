import pathlib
from typing import List

from pymongo import MongoClient

from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_sampler.services.notice_selectors import get_notice_ids_by_form_number, \
    get_notice_ids_by_eforms_subtype
from ted_sws.data_sampler.services.notice_xml_indexer import get_most_representative_notices
from ted_sws.resources.mapping_files_registry import MappingFilesRegistry

FORM_NUMBER_COLUMN_NAME = "form_number"
EFORMS_SUBTYPE_COLUMN_NAME = "eforms_subtype"
RESULT_NOTICE_SAMPLES_FOLDER_NAME = "notice_samples"


def store_notice_samples_in_file_system(mongodb_client: MongoClient, storage_path: pathlib.Path, top_k: int = None):
    """
        This function store notice samples in file system. Notices are selected by form number and eforms_subtypes.
    :param mongodb_client:
    :param storage_path:
    :param top_k:
    :return:
    """
    storage_path = storage_path / RESULT_NOTICE_SAMPLES_FOLDER_NAME
    storage_path.mkdir(parents=True, exist_ok=True)
    sf_notice_df = MappingFilesRegistry().sf_notice_df
    form_numbers = list(set(sf_notice_df[FORM_NUMBER_COLUMN_NAME].values.tolist()))
    eforms_subtypes = list(set(sf_notice_df[EFORMS_SUBTYPE_COLUMN_NAME].values.tolist()))
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)

    def store_samples_by_notice_ids(storage_samples_path: pathlib.Path, notice_ids: List[str]):
        most_representative_notice_ids = get_most_representative_notices(notice_ids=notice_ids,
                                                                         mongodb_client=mongodb_client,
                                                                         top_k=top_k
                                                                         )
        for notice_id in most_representative_notice_ids:
            notice = notice_repository.get(reference=notice_id)
            notice_xml_manifestation_file_path = storage_samples_path / f"{notice_id}.xml"
            with notice_xml_manifestation_file_path.open(mode="w", encoding="utf-8") as file:
                file.write(notice.xml_manifestation.object_data)

    for form_number in form_numbers:
        notice_samples_path = storage_path / f"form_number_{form_number}"
        notice_samples_path.mkdir(parents=True, exist_ok=True)
        selected_notice_ids = get_notice_ids_by_form_number(form_number=form_number,
                                                            mongodb_client=mongodb_client)
        store_samples_by_notice_ids(storage_samples_path=notice_samples_path, notice_ids=selected_notice_ids)

    for eforms_subtype in eforms_subtypes:
        notice_samples_path = storage_path / f"eforms_subtype_{eforms_subtype}"
        notice_samples_path.mkdir(parents=True, exist_ok=True)
        selected_notice_ids = get_notice_ids_by_eforms_subtype(eforms_subtype=eforms_subtype,
                                                               mongodb_client=mongodb_client)
        store_samples_by_notice_ids(storage_samples_path=notice_samples_path, notice_ids=selected_notice_ids)
