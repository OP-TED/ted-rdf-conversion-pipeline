import abc
from typing import Optional

import gridfs
from bson import ObjectId
from pymongo import MongoClient, ASCENDING

from ted_sws import config
from ted_sws.core.model.manifestation import Manifestation, RDFManifestation, XMLManifestation, METSManifestation
from ted_sws.data_manager.adapters.repository_abc import ManifestationRepositoryABC

MONGODB_COLLECTION_ID = "_id"
FILE_STORAGE_COLLECTION_NAME = "fs.files"
MANIFESTATION_ID = "manifestation_id"
OBJECT_DATA_KEY = "object_data"
AGGREGATE_REFERENCE_ID = "ted_id"
MANIFESTATION_TYPE_ID = "manifestation_type"


class BaseManifestationRepository(ManifestationRepositoryABC):
    _collection_name = "notice_manifestations"
    _manifestation_type = "unknown"

    def __init__(self, mongodb_client: MongoClient, database_name: str = None):
        database_name = database_name if database_name else config.MONGO_DB_AGGREGATES_DATABASE_NAME
        self._database_name = database_name
        self.mongodb_client = mongodb_client
        db = mongodb_client[self._database_name]
        self.file_storage = gridfs.GridFS(db)  # TODO: Investigate how it works in multiple processes in parallel.
        self.collection = db[self._collection_name]
        self.collection.create_index([(AGGREGATE_REFERENCE_ID, ASCENDING)])
        self.file_storage_collection = db[FILE_STORAGE_COLLECTION_NAME]
        self.file_storage_collection.create_index([(MANIFESTATION_ID,
                                                    ASCENDING)])  # TODO: index creation may bring race condition error.

    def _get_file_content_from_grid_fs(self, file_id: str) -> str:
        """
            This method load file_content from GridFS by field_id.
        :param file_id:
        :return:
        """
        return self.file_storage.get(file_id=ObjectId(file_id)).read().decode("utf-8")

    def _put_file_content_in_grid_fs(self, file_reference: str, file_content: str) -> ObjectId:
        """
            This method store file_content in GridFS and set notice_id as file metadata.
        :param file_reference:
        :param file_content:
        :return:
        """
        return self.file_storage.put(data=file_content.encode("utf-8"), file_reference=file_reference)

    def _update_manifestation(self, reference: str, manifestation: Manifestation, upsert: bool = False):
        """

        :param reference:
        :param manifestation:
        :param upsert:
        :return:
        """
        if manifestation is not None:
            manifestation_dict = manifestation.dict()
            manifestation_dict[AGGREGATE_REFERENCE_ID] = reference
            manifestation_dict[MANIFESTATION_TYPE_ID] = self._manifestation_type
            reference = self._build_reference(base_reference=reference)
            manifestation_dict[MONGODB_COLLECTION_ID] = reference
            old_linked_manifestation_file = self.file_storage.find_one({MANIFESTATION_ID: reference})
            manifestation_dict[OBJECT_DATA_KEY] = self._put_file_content_in_grid_fs(file_reference=reference,
                                                                                    file_content=manifestation_dict[
                                                                                        OBJECT_DATA_KEY])
            self.collection.update_one({MONGODB_COLLECTION_ID: reference}, {"$set": manifestation_dict}, upsert=upsert)
            if old_linked_manifestation_file is not None:
                self.file_storage.delete(file_id=old_linked_manifestation_file._id)

    def _get_manifestation_dict(self, reference: str) -> Optional[dict]:
        reference = self._build_reference(base_reference=reference)
        result_dict = self.collection.find_one({MONGODB_COLLECTION_ID: reference})
        if result_dict:
            result_dict[OBJECT_DATA_KEY] = self._get_file_content_from_grid_fs(file_id=result_dict[OBJECT_DATA_KEY])
            del result_dict[MONGODB_COLLECTION_ID]
            del result_dict[AGGREGATE_REFERENCE_ID]
            del result_dict[MANIFESTATION_TYPE_ID]
        return result_dict

    def _build_reference(self, base_reference: str) -> str:
        """

        :param base_reference:
        :return:
        """
        return f"{base_reference}_{self._manifestation_type}"

    @abc.abstractmethod
    def _build_manifestation_from_dict(self, manifestation_dict: dict) -> Manifestation:
        """

        :param manifestation_dict:
        :return:
        """

    def add(self, reference: str, manifestation: Manifestation):
        """

        :param reference:
        :param manifestation:
        :return:
        """
        self._update_manifestation(reference=reference, manifestation=manifestation, upsert=True)

    def update(self, reference: str, manifestation: Manifestation):
        """

        :param reference:
        :param manifestation:
        :return:
        """
        self._update_manifestation(reference=reference, manifestation=manifestation)

    def get(self, reference: str) -> Optional[Manifestation]:
        """

        :param reference:
        :return:
        """
        result_dict = self._get_manifestation_dict(reference=reference)
        if result_dict is not None:
            return self._build_manifestation_from_dict(manifestation_dict=result_dict)
        return None

    def remove(self, reference: str):
        """
            This method remove a manifestation based on an identification reference.
        :param reference:
        :return:
        """
        reference = self._build_reference(reference)
        self.collection.delete_one({MONGODB_COLLECTION_ID: reference})


class RDFManifestationRepository(BaseManifestationRepository):
    _manifestation_type: str = "rdf"

    def _build_manifestation_from_dict(self, manifestation_dict: dict) -> Manifestation:
        return RDFManifestation(**manifestation_dict)


class DistilledRDFManifestationRepository(RDFManifestationRepository):
    _manifestation_type: str = "distilled_rdf"


class XMLManifestationRepository(BaseManifestationRepository):
    _manifestation_type: str = "xml"

    def _build_manifestation_from_dict(self, manifestation_dict: dict) -> Manifestation:
        return XMLManifestation(**manifestation_dict)


class METSManifestationRepository(BaseManifestationRepository):
    _manifestation_type: str = "mets"

    def _build_manifestation_from_dict(self, manifestation_dict: dict) -> Manifestation:
        return METSManifestation(**manifestation_dict)
