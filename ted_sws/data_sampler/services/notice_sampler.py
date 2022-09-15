import pathlib
from typing import List

from pymongo import MongoClient

from ted_sws.core.adapters.cmd_runner import CmdRunner
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_sampler.services.notice_selectors import get_notice_ids_by_form_number, \
    get_notice_ids_by_eforms_subtype
from ted_sws.data_sampler.services.notice_xml_indexer import get_most_representative_notices
from ted_sws.resources.mapping_files_registry import MappingFilesRegistry

FORM_NUMBER_COLUMN_NAME = "form_number"
EFORMS_SUBTYPE_COLUMN_NAME = "eforms_subtype"
RESULT_NOTICE_SAMPLES_FOLDER_NAME = "notice_samples"
RUNNER_NAME = "NOTICE_SAMPLER_RUNNER"


class NoticeSamplerRunner(CmdRunner):

    def __init__(self, mongodb_client: MongoClient, storage_path: pathlib.Path,notice_filter:dict = None, top_k: int = None):
        """

        :param mongodb_client:
        :param storage_path:
        :param top_k:
        """
        super().__init__(name=RUNNER_NAME)
        self.top_k = top_k
        self.mongodb_client = mongodb_client
        self.notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        self.storage_path = storage_path / RESULT_NOTICE_SAMPLES_FOLDER_NAME
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.sf_notice_df = MappingFilesRegistry().sf_notice_df
        self.notice_filter = notice_filter

    def _store_samples_by_notice_ids(self, storage_samples_path: pathlib.Path, notice_ids: List[str]):
        """
            This method stores notices in the file system.
        :param storage_samples_path:
        :param notice_ids:
        :return:
        """
        if len(notice_ids):
            self.log(message=f"Get most representative notices from {len(notice_ids)} notices...")
            most_representative_notice_ids = get_most_representative_notices(notice_ids=notice_ids,
                                                                             mongodb_client=self.mongodb_client,
                                                                             top_k=self.top_k
                                                                             )
            self.log_success_msg(msg=f"Retrieved {len(most_representative_notice_ids)} most representative notices.")
            self.log(
                message=f"Start store K={len(most_representative_notice_ids)} samples in folder [{storage_samples_path.name}]...")
            for notice_id in most_representative_notice_ids:
                notice = self.notice_repository.get(reference=notice_id)
                notice_xml_manifestation_file_path = storage_samples_path / f"{notice_id}.xml"
                with notice_xml_manifestation_file_path.open(mode="w", encoding="utf-8") as file:
                    file.write(notice.xml_manifestation.object_data)
            self.log_success_msg(
                msg=f"Finish store K={len(most_representative_notice_ids)} samples in folder [{storage_samples_path.name}]!")

    def execute_notice_sampler_foreach_form_number(self):
        """
            This method executes notice sampler for each form_number.
        :return:
        """
        form_numbers = list(set(self.sf_notice_df[FORM_NUMBER_COLUMN_NAME].values.tolist()))
        self.log(message="Start notice sampler for form_numbers:")
        for form_number in form_numbers:
            notice_samples_path = self.storage_path / f"form_number_{form_number}"
            notice_samples_path.mkdir(parents=True, exist_ok=True)
            self.log(message="-" * 50)
            self.log(message=f"Get notice_ids by form_number = [{form_number}]...")
            selected_notice_ids = get_notice_ids_by_form_number(form_number=form_number,
                                                                mongodb_client=self.mongodb_client,
                                                                notice_filter=self.notice_filter
                                                                )
            self.log(message=f"Retrieved {len(selected_notice_ids)} notice_ids by form_number = [{form_number}]...")
            self._store_samples_by_notice_ids(storage_samples_path=notice_samples_path, notice_ids=selected_notice_ids)
            self.log(message="-" * 50)
        self.log(message="Finish notice sampler for form_numbers.")

    def execute_notice_sampler_foreach_eforms_subtype(self):
        """
            This method executes notice sampler for each eforms_subtype.
        :return:
        """
        eforms_subtypes = list(set(self.sf_notice_df[EFORMS_SUBTYPE_COLUMN_NAME].values.tolist()))
        self.log(message="Start notice sampler for eforms_subtypes:")
        for eforms_subtype in eforms_subtypes:
            notice_samples_path = self.storage_path / f"eforms_subtype_{eforms_subtype}"
            notice_samples_path.mkdir(parents=True, exist_ok=True)
            self.log(message="-" * 50)
            self.log(message=f"Get notice_ids by eforms_subtype = [{eforms_subtype}]...")
            selected_notice_ids = get_notice_ids_by_eforms_subtype(eforms_subtype=str(eforms_subtype),
                                                                   mongodb_client=self.mongodb_client,
                                                                   notice_filter=self.notice_filter
                                                                   )
            self.log(
                message=f"Retrieved {len(selected_notice_ids)} notice_ids by eforms_subtype = [{eforms_subtype}]...")
            self._store_samples_by_notice_ids(storage_samples_path=notice_samples_path, notice_ids=selected_notice_ids)
            self.log(message="-" * 50)
        self.log(message="Finish notice sampler for eforms_subtypes.")

    def run_cmd(self):
        """
            This method notifies the sampler for each form_number and eforms_subtype.
        :return:
        """
        self.execute_notice_sampler_foreach_eforms_subtype()
        self.execute_notice_sampler_foreach_form_number()


def store_notice_samples_in_file_system(mongodb_client: MongoClient, storage_path: pathlib.Path,
                                        notice_filter: dict = None, top_k: int = None):
    """
        This function store notice samples in file system. Notices are selected by form number and eforms_subtypes.
    :param mongodb_client:
    :param storage_path:
    :param notice_filter:
    :param top_k:
    :return:
    """
    notice_sampler = NoticeSamplerRunner(mongodb_client=mongodb_client,
                                         storage_path=storage_path,
                                         notice_filter=notice_filter,
                                         top_k=top_k
                                         )
    notice_sampler.run()
