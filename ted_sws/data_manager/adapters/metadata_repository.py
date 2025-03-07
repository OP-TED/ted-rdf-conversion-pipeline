import abc
from typing import Optional

from pymongo import MongoClient, ASCENDING

from ted_sws import config
from ted_sws.core.model.metadata import Metadata, NormalisedMetadata, TEDMetadata, XMLMetadata
from ted_sws.data_manager.adapters.repository_abc import MetadataRepositoryABC

MONGODB_COLLECTION_ID = "_id"
AGGREGATE_REFERENCE_ID = "ted_id"
METADATA_TYPE_ID = "metadata_type"


class BaseMetadataRepository(MetadataRepositoryABC, abc.ABC):
    """
       This repository is intended for storing Metadata objects.
    """
    _collection_name: str = "notice_metadata"
    _metadata_type: str = "unknown"

    def __init__(self, mongodb_client: MongoClient, database_name: str = None):
        database_name = database_name if database_name else config.MONGO_DB_AGGREGATES_DATABASE_NAME
        self._database_name = database_name
        self.mongodb_client = mongodb_client
        db = mongodb_client[self._database_name]
        self.collection = db[self._collection_name]
        self.collection.create_index([(AGGREGATE_REFERENCE_ID, ASCENDING)])
        self.collection.create_index([(METADATA_TYPE_ID, ASCENDING)])

    def _update_metadata(self, reference: str, metadata: Metadata, upsert: bool = False):
        """

        :param reference:
        :param metadata:
        :param upsert:
        :return:
        """
        if metadata is not None:
            metadata_dict = metadata.dict()
            metadata_dict[AGGREGATE_REFERENCE_ID] = reference
            metadata_dict[METADATA_TYPE_ID] = self._metadata_type
            reference = self._build_reference(base_reference=reference)
            metadata_dict[MONGODB_COLLECTION_ID] = reference
            self.collection.update_one({MONGODB_COLLECTION_ID: reference}, {"$set": metadata_dict}, upsert=upsert)

    def _get_metadata_dict(self, reference: str) -> Optional[dict]:
        """

        :param reference:
        :return:
        """
        reference = self._build_reference(base_reference=reference)
        result_dict = self.collection.find_one({MONGODB_COLLECTION_ID: reference})
        if result_dict:
            del result_dict[MONGODB_COLLECTION_ID]
            del result_dict[AGGREGATE_REFERENCE_ID]
            del result_dict[METADATA_TYPE_ID]
        return result_dict

    def _build_reference(self, base_reference: str) -> str:
        """

        :param base_reference:
        :return:
        """
        return f"{base_reference}_{self._metadata_type}"


    def remove(self, reference: str):
        """
            This method remove a metadata based on an identification reference.
        :param reference:
        :return:
        """
        reference = self._build_reference(reference)
        self.collection.delete_one({MONGODB_COLLECTION_ID: reference})


class NormalisedMetadataRepository(BaseMetadataRepository):
    _metadata_type: str = "normalised"

    def add(self, reference: str, metadata: NormalisedMetadata):
        """
            This method allows you to add normalised metadata objects to the repository.
        :param reference:
        :param metadata:
        :return:
        """
        self._update_metadata(reference=reference, metadata=metadata, upsert=True)

    def update(self, reference: str, metadata: NormalisedMetadata):
        """
            This method allows you to update normalised metadata objects to the repository
        :param reference:
        :param metadata:
        :return:
        """

        self._update_metadata(reference=reference, metadata=metadata)

    def get(self, reference: str) -> Optional[NormalisedMetadata]:
        """
            This method allows a normalised metadata to be obtained based on an identification reference.
        :param reference:
        :return: Metadata
        """

        result_dict = self._get_metadata_dict(reference=reference)
        if result_dict is not None:
            return NormalisedMetadata(**result_dict)
        return None


class TEDMetadataRepository(BaseMetadataRepository):
    _metadata_type: str = "ted"

    def add(self, reference: str, metadata: TEDMetadata):
        """
            This method allows you to add ted metadata objects to the repository.
        :param reference:
        :param metadata:
        :return:
        """
        self._update_metadata(reference=reference, metadata=metadata, upsert=True)

    def update(self, reference: str, metadata: TEDMetadata):
        """
            This method allows you to update ted metadata objects to the repository
        :param reference:
        :param metadata:
        :return:
        """
        self._update_metadata(reference=reference, metadata=metadata)

    def get(self, reference: str) -> Optional[TEDMetadata]:
        """
            This method allows a ted metadata to be obtained based on an identification reference.
        :param reference:
        :return: Metadata
        """

        result_dict = self._get_metadata_dict(reference=reference)
        if result_dict is not None:
            return TEDMetadata(**result_dict)
        return None


class XMLMetadataRepository(BaseMetadataRepository):
    _metadata_type: str = "xml"

    def add(self, reference: str, metadata: XMLMetadata):
        """
            This method allows you to add xml metadata objects to the repository.
        :param reference:
        :param metadata:
        :return:
        """
        self._update_metadata(reference=reference, metadata=metadata, upsert=True)

    def update(self, reference: str, metadata: XMLMetadata):
        """
            This method allows you to update xml metadata objects to the repository
        :param reference:
        :param metadata:
        :return:
        """

        self._update_metadata(reference=reference, metadata=metadata)

    def get(self, reference: str) -> Optional[XMLMetadata]:
        """
            This method allows a xml metadata to be obtained based on an identification reference.
        :param reference:
        :return: Metadata
        """

        result_dict = self._get_metadata_dict(reference=reference)
        if result_dict is not None:
            return XMLMetadata(**result_dict)
        return None
