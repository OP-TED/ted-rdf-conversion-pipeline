import copy
from datetime import datetime
import logging
from typing import Iterator, Union, Optional, Tuple

import gridfs
from pymongo import MongoClient, ASCENDING
from bson import ObjectId
from ted_sws import config
from ted_sws.core.model.manifestation import XMLManifestation, RDFManifestation, METSManifestation, Manifestation
from ted_sws.core.model.metadata import NormalisedMetadata
from ted_sws.data_manager.adapters.repository_abc import NoticeRepositoryABC
from ted_sws.core.model.notice import Notice, NoticeStatus

logger = logging.getLogger(__name__)

MONGODB_COLLECTION_ID = "_id"
NOTICE_TED_ID = "ted_id"
NOTICE_STATUS = "status"
NOTICE_CREATED_AT = "created_at"
NOTICE_NORMALISED_METADATA = "normalised_metadata"
NOTICE_PREPROCESSED_XML_MANIFESTATION = "preprocessed_xml_manifestation"
NOTICE_DISTILLED_RDF_MANIFESTATION = "distilled_rdf_manifestation"
NOTICE_RDF_MANIFESTATION = "rdf_manifestation"
NOTICE_METS_MANIFESTATION = "mets_manifestation"
METADATA_PUBLICATION_DATE = "publication_date"
METADATA_DOCUMENT_SENT_DATE = "document_sent_date"


class NoticeRepository(NoticeRepositoryABC):
    """
       This repository is intended for storing Notice objects.
    """

    _collection_name = "notice_collection"
    _database_name = config.MONGO_DB_AGGREGATES_DATABASE_NAME

    def __init__(self, mongodb_client: MongoClient, database_name: str = _database_name):
        self._database_name = database_name
        self.mongodb_client = mongodb_client
        notice_db = mongodb_client[self._database_name]
        self.file_storage = gridfs.GridFS(notice_db)
        self.collection = notice_db[self._collection_name]
        self.file_storage_collection = notice_db["fs.files"]
        self.file_storage_collection.create_index([("notice_id", ASCENDING)])

    def get_file_content_from_grid_fs(self, file_id: str) -> str:
        """
            This method load file_content from GridFS by field_id.
        :param file_id:
        :return:
        """
        return self.file_storage.get(file_id=ObjectId(file_id)).read().decode("utf-8")

    def put_file_content_in_grid_fs(self, notice_id: str, file_content: str) -> ObjectId:
        """
            This method store file_content in GridFS and set notice_id as file metadata.
        :param notice_id:
        :param file_content:
        :return:
        """
        return self.file_storage.put(data=file_content.encode("utf-8"), notice_id=notice_id)

    def delete_files_by_notice_id(self, linked_file_ids: list):
        """
            This method delete all files from GridFS with specific notice_id in metadata.
        :param linked_file_ids:
        :return:
        """
        for linked_file_id in linked_file_ids:
            self.file_storage.delete(file_id=linked_file_id)

    def write_notice_fields_in_grid_fs(self, notice: Notice) -> Tuple[Notice, list, list]:
        """
            This method store large fields in GridFS.
        :param notice:
        :return:
        """
        notice = copy.deepcopy(notice)
        linked_file_ids = [linked_file._id for linked_file in
                           self.file_storage.find({"notice_id": notice.ted_id})]

        new_linked_file_ids = []

        def write_large_field(large_field: Manifestation):
            if (large_field is not None) and (large_field.object_data is not None):
                object_id = self.put_file_content_in_grid_fs(notice_id=notice.ted_id,
                                                             file_content=large_field.object_data)
                large_field.object_data = str(object_id)
                new_linked_file_ids.append(object_id)

        write_large_field(notice.xml_manifestation)
        write_large_field(notice.rdf_manifestation)
        write_large_field(notice.mets_manifestation)
        write_large_field(notice.distilled_rdf_manifestation)
        write_large_field(notice.preprocessed_xml_manifestation)
        if notice.rdf_manifestation:
            for validation_report in notice.rdf_manifestation.shacl_validations:
                write_large_field(validation_report)

            for validation_report in notice.rdf_manifestation.sparql_validations:
                write_large_field(validation_report)

        if notice.distilled_rdf_manifestation:
            for validation_report in notice.distilled_rdf_manifestation.shacl_validations:
                write_large_field(validation_report)

            for validation_report in notice.distilled_rdf_manifestation.sparql_validations:
                write_large_field(validation_report)

        return notice, linked_file_ids, new_linked_file_ids

    def load_notice_fields_from_grid_fs(self, notice: Notice) -> Notice:
        """
           This method loads large fields from GridFS.
        :param notice:
        :return:
        """

        def load_large_field(large_field: Manifestation):
            if (large_field is not None) and (large_field.object_data is not None):
                large_field.object_data = self.get_file_content_from_grid_fs(file_id=large_field.object_data)

        load_large_field(large_field=notice.xml_manifestation)
        load_large_field(large_field=notice.rdf_manifestation)
        load_large_field(large_field=notice.mets_manifestation)
        load_large_field(large_field=notice.distilled_rdf_manifestation)
        load_large_field(large_field=notice.preprocessed_xml_manifestation)
        if notice.rdf_manifestation:
            for validation_report in notice.rdf_manifestation.shacl_validations:
                load_large_field(validation_report)
            for validation_report in notice.rdf_manifestation.sparql_validations:
                load_large_field(validation_report)

        if notice.distilled_rdf_manifestation:
            for validation_report in notice.distilled_rdf_manifestation.shacl_validations:
                load_large_field(validation_report)

            for validation_report in notice.distilled_rdf_manifestation.sparql_validations:
                load_large_field(validation_report)

        return notice

    @staticmethod
    def _create_notice_from_repository_result(notice_dict: dict) -> Union[Notice, None]:
        """
            This method allows you to create a Notice from the dictionary extracted from the repository.
        :param notice_dict:
        :return:
        """

        def init_object_from_dict(object_class, key):
            if notice_dict[key]:
                return object_class(**notice_dict[key])
            return None

        def date_field_to_string(date_field: datetime):
            if date_field:
                return date_field.isoformat()
            return None

        if notice_dict:
            del notice_dict[MONGODB_COLLECTION_ID]
            notice_dict[NOTICE_CREATED_AT] = notice_dict[NOTICE_CREATED_AT].isoformat()
            if notice_dict[NOTICE_NORMALISED_METADATA]:
                notice_dict[NOTICE_NORMALISED_METADATA][METADATA_PUBLICATION_DATE] = date_field_to_string(
                    notice_dict[NOTICE_NORMALISED_METADATA][METADATA_PUBLICATION_DATE])
                notice_dict[NOTICE_NORMALISED_METADATA][METADATA_DOCUMENT_SENT_DATE] = date_field_to_string(
                    notice_dict[NOTICE_NORMALISED_METADATA][METADATA_DOCUMENT_SENT_DATE])

            notice = Notice(**notice_dict)
            notice._status = NoticeStatus[notice_dict[NOTICE_STATUS]]
            notice._normalised_metadata = init_object_from_dict(NormalisedMetadata, NOTICE_NORMALISED_METADATA)
            notice._preprocessed_xml_manifestation = init_object_from_dict(XMLManifestation,
                                                                           NOTICE_PREPROCESSED_XML_MANIFESTATION)
            notice._distilled_rdf_manifestation = init_object_from_dict(RDFManifestation,
                                                                        NOTICE_DISTILLED_RDF_MANIFESTATION)
            notice._rdf_manifestation = init_object_from_dict(RDFManifestation, NOTICE_RDF_MANIFESTATION)
            notice._mets_manifestation = init_object_from_dict(METSManifestation, NOTICE_METS_MANIFESTATION)
            return notice
        return None

    @staticmethod
    def _create_dict_from_notice(notice: Notice) -> dict:
        """
            This method allows you to create a dictionary that can be stored in a repository based on a Notice.
        :param notice:
        :return:
        """

        notice_dict = notice.dict()
        notice_dict[MONGODB_COLLECTION_ID] = notice_dict[NOTICE_TED_ID]
        notice_dict[NOTICE_STATUS] = str(notice_dict[NOTICE_STATUS])
        notice_dict[NOTICE_CREATED_AT] = datetime.fromisoformat(notice_dict[NOTICE_CREATED_AT])

        if notice_dict[NOTICE_NORMALISED_METADATA]:
            if notice_dict[NOTICE_NORMALISED_METADATA][METADATA_PUBLICATION_DATE]:
                notice_dict[NOTICE_NORMALISED_METADATA][METADATA_PUBLICATION_DATE] = datetime.fromisoformat(
                    notice_dict[NOTICE_NORMALISED_METADATA][METADATA_PUBLICATION_DATE])
            if notice_dict[NOTICE_NORMALISED_METADATA][METADATA_DOCUMENT_SENT_DATE]:
                notice_dict[NOTICE_NORMALISED_METADATA][METADATA_DOCUMENT_SENT_DATE] = datetime.fromisoformat(
                    notice_dict[NOTICE_NORMALISED_METADATA][METADATA_DOCUMENT_SENT_DATE])

        return notice_dict

    def _update_notice(self, notice: Notice, upsert: bool = False):
        notice, linked_file_ids, new_linked_file_ids = self.write_notice_fields_in_grid_fs(notice=notice)
        notice_dict = NoticeRepository._create_dict_from_notice(notice=notice)
        try:
            self.collection.update_one({MONGODB_COLLECTION_ID: notice_dict[MONGODB_COLLECTION_ID]},
                                       {"$set": notice_dict}, upsert=upsert)
            self.delete_files_by_notice_id(linked_file_ids=linked_file_ids)
        except Exception as exception:
            self.delete_files_by_notice_id(linked_file_ids=new_linked_file_ids)
            raise exception

    def add(self, notice: Notice):
        """
            This method allows you to add notice objects to the repository.
        :param notice:
        :return:
        """
        self._update_notice(notice=notice, upsert=True)

    def update(self, notice: Notice):
        """
            This method allows you to update notice objects to the repository
        :param notice:
        :return:
        """
        notice_exist = self.collection.find_one({MONGODB_COLLECTION_ID: notice.ted_id})
        if notice_exist is not None:
            self._update_notice(notice=notice)

    def get(self, reference) -> Optional[Notice]:
        """
            This method allows a notice to be obtained based on an identification reference.
        :param reference:
        :return: Notice
        """
        result_dict = self.collection.find_one({MONGODB_COLLECTION_ID: reference})
        if result_dict is not None:
            notice = NoticeRepository._create_notice_from_repository_result(result_dict)
            notice = self.load_notice_fields_from_grid_fs(notice)
            return notice
        return None

    def get_notice_by_status(self, notice_status: NoticeStatus) -> Iterator[Notice]:
        """
            This method provides all notices based on its status.
        :param notice_status:
        :return:
        """
        for result_dict in self.collection.find({NOTICE_STATUS: str(notice_status)}):
            notice = NoticeRepository._create_notice_from_repository_result(result_dict)
            notice = self.load_notice_fields_from_grid_fs(notice)
            yield notice

    def list(self) -> Iterator[Notice]:
        """
            This method allows all records to be retrieved from the repository.
        :return: list of notices
        """
        for result_dict in self.collection.find():
            notice = NoticeRepository._create_notice_from_repository_result(result_dict)
            notice = self.load_notice_fields_from_grid_fs(notice)
            yield notice
