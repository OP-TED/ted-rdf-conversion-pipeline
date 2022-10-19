import itertools
import pathlib
from typing import Union

from pymongo import MongoClient
from ted_sws import config
from ted_sws.core.model.supra_notice import DailySupraNotice
from ted_sws.data_manager.adapters.supra_notice_repository import DailySupraNoticeRepository


def unpack_supra_notice(supra_notice: DailySupraNotice, unpack_path: pathlib.Path):
    def write_in_file(data: Union[str, bytes], terminal_path: str):
        write_path = unpack_path / terminal_path
        if type(data) == str:
            write_path.write_text(data=data, encoding="utf-8")
        elif type(data) == bytes:
            write_path.write_bytes(data)

    write_in_file(supra_notice.validation_summary.object_data, "validation_summary.html")


def test_supra_notice_unpacking_in_file_system():
    uri = config.MONGO_DB_AUTH_URL
    mongodb_client = MongoClient(uri)
    supra_notice_repository = DailySupraNoticeRepository(mongodb_client=mongodb_client)
    unpacking_folder = pathlib.Path("./unpacking_supra_notice_result")
    for index, supra_notice in enumerate(itertools.islice(supra_notice_repository.list(), 5)):
        supra_notice_unpacking_folder = unpacking_folder / f"supra_notice_{supra_notice.notice_fetched_date.strftime('%Y_%m_%d')}"
        supra_notice_unpacking_folder.mkdir(parents=True, exist_ok=True)
        unpack_supra_notice(supra_notice=supra_notice, unpack_path=supra_notice_unpacking_folder)
