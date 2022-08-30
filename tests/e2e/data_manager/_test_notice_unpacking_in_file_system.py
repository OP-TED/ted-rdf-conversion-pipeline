import base64
import json
import pathlib
from typing import Union

from pymongo import MongoClient

from ted_sws import config
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository


def unpack_notice(notice: Notice, unpack_path: pathlib.Path):
    def write_in_file(data: Union[str, bytes], terminal_path: str):
        write_path = unpack_path / terminal_path
        if type(data) == str:
            write_path.write_text(data=data, encoding="utf-8")
        elif type(data) == bytes:
            write_path.write_bytes(data)

    write_in_file(notice.rdf_manifestation.object_data, "rdf_manifestation.ttl")
    write_in_file(notice.distilled_rdf_manifestation.object_data, "distilled_rdf_manifestation.ttl")
    write_in_file(notice.xml_manifestation.object_data, "xml_manifestation.xml")
    write_in_file(base64.b64decode(notice.mets_manifestation.object_data.encode(encoding="utf-8")),
                  "mets_manifestation.zip")

    for shacl_validation in notice.rdf_manifestation.shacl_validations:
        write_in_file(shacl_validation.object_data, "shacl_validation.html")
        shacl_validation_json = json.dumps(shacl_validation.validation_results.dict())
        write_in_file(shacl_validation_json, "shacl_validation.json")

    for sparql_validation in notice.rdf_manifestation.sparql_validations:
        write_in_file(sparql_validation.object_data, "sparql_validation.html")
        sparql_validation_json = json.dumps(
            [validation_result.dict() for validation_result in sparql_validation.validation_results])
        write_in_file(sparql_validation_json, "sparql_validation.json")


def test_notice_unpacking_in_file_system():
    uri = "MONGODB_AUTH_URL"
    mongodb_client = MongoClient(uri)
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    unpacking_folder = pathlib.Path("./unpacking_result")
    for notice in notice_repository.list():
        if notice.status == NoticeStatus.PACKAGED:
            notice_unpacking_folder = unpacking_folder / notice.ted_id
            notice_unpacking_folder.mkdir(parents=True, exist_ok=True)
            unpack_notice(notice=notice, unpack_path=notice_unpacking_folder)
