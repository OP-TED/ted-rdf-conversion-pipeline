import copy
import json
import logging
import pathlib
from datetime import datetime
from typing import Iterator, Union, Optional, Tuple, Any

import gridfs
from bson import ObjectId
from pymongo import MongoClient, ASCENDING

from ted_sws import config
from ted_sws.core.model.lazy_object import LazyObjectFieldsLoaderABC
from ted_sws.core.model.manifestation import XMLManifestation, RDFManifestation, METSManifestation, Manifestation
from ted_sws.core.model.metadata import NormalisedMetadata, TEDMetadata, Metadata, XMLMetadata
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.data_manager.adapters import inject_date_string_fields, remove_date_string_fields
from ted_sws.data_manager.adapters.manifestation_repository import XMLManifestationRepository, \
    RDFManifestationRepository, METSManifestationRepository, DistilledRDFManifestationRepository
from ted_sws.data_manager.adapters.metadata_repository import NormalisedMetadataRepository, TEDMetadataRepository, \
    XMLMetadataRepository
from ted_sws.data_manager.adapters.repository_abc import NoticeRepositoryABC
from ted_sws.notice_metadata_processor.services.metadata_normalizer import create_normalised_metadata_view

logger = logging.getLogger(__name__)

MONGODB_COLLECTION_ID = "_id"

NOTICE_TED_ID = "ted_id"
NOTICE_STATUS = "status"
NOTICE_CREATED_AT = "created_at"
NOTICE_ID = "notice_id"
NOTICE_NORMALISED_METADATA = "normalised_metadata"
NOTICE_PREPROCESSED_XML_MANIFESTATION = "preprocessed_xml_manifestation"
NOTICE_DISTILLED_RDF_MANIFESTATION = "distilled_rdf_manifestation"
NOTICE_RDF_MANIFESTATION = "rdf_manifestation"
NOTICE_METS_MANIFESTATION = "mets_manifestation"
NOTICE_TED_METADATA = "original_metadata"
NOTICE_XML_MANIFESTATION = "xml_manifestation"
NOTICE_XML_METADATA = "xml_metadata"
VALIDATION_SUMMARY = "validation_summary"

METADATA_PUBLICATION_DATE = "publication_date"
METADATA_DOCUMENT_SENT_DATE = "document_sent_date"

NOTICE_ORIGINAL_METADATA_PRIVATE_KEY = "_original_metadata"
NOTICE_NORMALISED_METADATA_PRIVATE_KEY = "_normalised_metadata"
NOTICE_XML_METADATA_PRIVATE_KEY = "_xml_metadata"
NOTICE_XML_MANIFESTATION_PRIVATE_KEY = "_xml_manifestation"
NOTICE_PREPROCESSED_XML_MANIFESTATION_KEY = "_preprocessed_xml_manifestation"
NOTICE_RDF_MANIFESTATION_PRIVATE_KEY = "_rdf_manifestation"
NOTICE_DISTILLED_RDF_MANIFESTATION_PRIVATE_KEY = "_distilled_rdf_manifestation"
NOTICE_METS_MANIFESTATION_PRIVATE_KEY = "_mets_manifestation"


class NoticeRepositoryInFileSystem(NoticeRepositoryABC):
    """
       This repository is intended for storing Notice objects as JSON files in file system.
    """

    def __init__(self, repository_path: pathlib.Path):
        self.repository_path = pathlib.Path(repository_path)
        self.repository_path.mkdir(parents=True, exist_ok=True)

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

        if notice_dict:
            notice = Notice(**notice_dict)
            notice._status = NoticeStatus[notice_dict[NOTICE_STATUS]]
            notice._original_metadata = init_object_from_dict(TEDMetadata, NOTICE_TED_METADATA)
            notice._xml_manifestation = init_object_from_dict(XMLManifestation, NOTICE_XML_MANIFESTATION)
            notice._normalised_metadata = init_object_from_dict(NormalisedMetadata, NOTICE_NORMALISED_METADATA)
            notice._preprocessed_xml_manifestation = init_object_from_dict(XMLManifestation,
                                                                           NOTICE_PREPROCESSED_XML_MANIFESTATION)
            notice._distilled_rdf_manifestation = init_object_from_dict(RDFManifestation,
                                                                        NOTICE_DISTILLED_RDF_MANIFESTATION)
            notice._rdf_manifestation = init_object_from_dict(RDFManifestation, NOTICE_RDF_MANIFESTATION)
            notice._mets_manifestation = init_object_from_dict(METSManifestation, NOTICE_METS_MANIFESTATION)
            notice._xml_metadata = init_object_from_dict(XMLMetadata, NOTICE_XML_METADATA)
            return notice
        return None

    def add(self, notice: Notice):
        """
            This method allows you to add notice objects to the repository.
        :param notice:
        :return:
        """
        notice_file_path = self.repository_path / f"{notice.ted_id}.json"
        notice_dict = notice.dict()
        notice_dict[NOTICE_STATUS] = str(notice_dict[NOTICE_STATUS])
        notice_file_path.write_text(data=json.dumps(notice_dict), encoding="utf-8")

    def update(self, notice: Notice):
        """
            This method allows you to update notice objects to the repository
        :param notice:
        :return:
        """
        self.add(notice=notice)

    @classmethod
    def _read_notice_from_file(cls, notice_file_path: pathlib.Path) -> Optional[Notice]:
        """
            This method provides the ability to read a notice from a JSON file.
        :param notice_file_path:
        :return:
        """
        if notice_file_path.exists() and notice_file_path.is_file():
            notice_dict = json.loads(notice_file_path.read_text(encoding="utf-8"))
            return NoticeRepositoryInFileSystem._create_notice_from_repository_result(notice_dict=notice_dict)
        else:
            return None

    def get(self, reference) -> Optional[Notice]:
        """
            This method allows a notice to be obtained based on an identification reference.
        :param reference:
        :return: Notice
        """
        notice_file_path = self.repository_path / f"{reference}.json"
        return self._read_notice_from_file(notice_file_path=notice_file_path)

    def list(self) -> Iterator[Notice]:
        """
            This method allows all records to be retrieved from the repository.
        :return: list of notices
        """
        for notice_file_path in self.repository_path.iterdir():
            if notice_file_path.is_file() and notice_file_path.suffix == ".json":
                yield self._read_notice_from_file(notice_file_path=notice_file_path)


class NoticeRepository(NoticeRepositoryABC, LazyObjectFieldsLoaderABC):
    """
       This repository is intended for storing Notice objects.
    """

    _collection_name = "notice_collection"

    def __init__(self, mongodb_client: MongoClient, database_name: str = None):
        database_name = database_name if database_name else config.MONGO_DB_AGGREGATES_DATABASE_NAME
        self._database_name = database_name
        self.mongodb_client = mongodb_client
        notice_db = mongodb_client[self._database_name]
        self.collection = notice_db[self._collection_name]
        self.collection.create_index(
            [(NOTICE_CREATED_AT, ASCENDING)])
        self.collection.create_index(
            [(NOTICE_STATUS, ASCENDING)])
        self.xml_manifestation_repository = XMLManifestationRepository(mongodb_client=mongodb_client,
                                                                       database_name=database_name)
        self.rdf_manifestation_repository = RDFManifestationRepository(mongodb_client=mongodb_client,
                                                                       database_name=database_name)
        self.distilled_rdf_manifestation_repository = DistilledRDFManifestationRepository(mongodb_client=mongodb_client,
                                                                                          database_name=database_name)
        self.mets_manifestation_repository = METSManifestationRepository(mongodb_client=mongodb_client,
                                                                         database_name=database_name)
        self.normalised_metadata_repository = NormalisedMetadataRepository(mongodb_client=mongodb_client,
                                                                           database_name=database_name)
        self.ted_metadata_repository = TEDMetadataRepository(mongodb_client=mongodb_client,
                                                             database_name=database_name)
        self.xml_metadata_repository = XMLMetadataRepository(mongodb_client=mongodb_client,
                                                             database_name=database_name)

    def _mapping_lazy_fields(self):
        return {
            Notice.original_metadata: (NOTICE_ORIGINAL_METADATA_PRIVATE_KEY,
                                       self.ted_metadata_repository),
            Notice.normalised_metadata: (NOTICE_NORMALISED_METADATA_PRIVATE_KEY,
                                         self.normalised_metadata_repository),
            Notice.xml_metadata: (NOTICE_XML_METADATA_PRIVATE_KEY,
                                  self.xml_metadata_repository),
            Notice.xml_manifestation: (NOTICE_XML_MANIFESTATION_PRIVATE_KEY,
                                       self.xml_manifestation_repository),
            # @Note: preprocessed_xml_manifestation at the moment is same as xml_manifestation
            # in this case is used same repository, in future need to create another repository
            Notice.preprocessed_xml_manifestation: (NOTICE_PREPROCESSED_XML_MANIFESTATION_KEY,
                                                    self.xml_manifestation_repository),
            Notice.rdf_manifestation: (NOTICE_RDF_MANIFESTATION_PRIVATE_KEY,
                                       self.rdf_manifestation_repository),
            Notice.distilled_rdf_manifestation: (NOTICE_DISTILLED_RDF_MANIFESTATION_PRIVATE_KEY,
                                                 self.distilled_rdf_manifestation_repository),
            Notice.mets_manifestation: (NOTICE_METS_MANIFESTATION_PRIVATE_KEY,
                                        self.mets_manifestation_repository)
        }

    def load_lazy_field(self, source_object: Notice, property_field: property) -> Any:
        """

        :param source_object:
        :param property_field:
        :return:
        """
        mapping_lazy_fields = self._mapping_lazy_fields()
        notice_field, field_repository = mapping_lazy_fields[property_field]
        notice_field_data = field_repository.get(source_object.ted_id)
        setattr(source_object, notice_field, notice_field_data)

    def remove_lazy_field(self, source_object: Any, property_field: property):
        mapping_lazy_fields = self._mapping_lazy_fields()
        notice_field, field_repository = mapping_lazy_fields[property_field]
        field_repository.remove(source_object.ted_id)
        setattr(source_object, notice_field, None)

    def _write_lazy_fields(self, notice: Notice):
        mapping_lazy_fields = self._mapping_lazy_fields()
        for notice_field, repository in mapping_lazy_fields.values():
            notice_field_data = getattr(notice, notice_field)
            if notice_field_data is not None:
                repository.add(notice.ted_id, notice_field_data)

    def _create_notice_from_repository_result(self, notice_dict: dict) -> Union[Notice, None]:
        """
            This method allows you to create a Notice from the dictionary extracted from the repository.
        :param notice_dict:
        :return:
        """
        if notice_dict:
            del notice_dict[MONGODB_COLLECTION_ID]
            notice_dict.pop(NOTICE_NORMALISED_METADATA, None)
            remove_date_string_fields(data=notice_dict, date_field_name=NOTICE_CREATED_AT)
            notice_dict[NOTICE_CREATED_AT] = notice_dict[NOTICE_CREATED_AT].isoformat()
            notice = Notice(**notice_dict)
            notice._status = NoticeStatus[notice_dict[NOTICE_STATUS]]
            notice.set_lazy_object_fields_loader(lazy_object_fields_loader=self)
            return notice
        return None

    @staticmethod
    def _create_dict_from_notice(notice: Notice) -> dict:
        """
            This method allows you to create a dictionary that can be stored in a repository based on a Notice.
        :param notice:
        :return:
        """

        notice_dict = notice.dict(include={NOTICE_TED_ID: True, NOTICE_STATUS: True,
                                           NOTICE_CREATED_AT: True, VALIDATION_SUMMARY: True})
        notice_dict[MONGODB_COLLECTION_ID] = notice_dict[NOTICE_TED_ID]
        notice_dict[NOTICE_STATUS] = str(notice_dict[NOTICE_STATUS])
        notice_dict[NOTICE_CREATED_AT] = datetime.fromisoformat(notice_dict[NOTICE_CREATED_AT])

        if notice._normalised_metadata:
            normalised_metadata_dict = create_normalised_metadata_view(notice._normalised_metadata).dict()
            if normalised_metadata_dict[METADATA_PUBLICATION_DATE]:
                normalised_metadata_dict[METADATA_PUBLICATION_DATE] = datetime.fromisoformat(
                    normalised_metadata_dict[METADATA_PUBLICATION_DATE])
                inject_date_string_fields(data=normalised_metadata_dict,
                                          date_field_name=METADATA_PUBLICATION_DATE)
            if normalised_metadata_dict:
                normalised_metadata_dict[METADATA_DOCUMENT_SENT_DATE] = datetime.fromisoformat(
                    normalised_metadata_dict[METADATA_DOCUMENT_SENT_DATE])
                inject_date_string_fields(data=normalised_metadata_dict,
                                          date_field_name=METADATA_DOCUMENT_SENT_DATE)
            notice_dict[NOTICE_NORMALISED_METADATA] = normalised_metadata_dict
        inject_date_string_fields(data=notice_dict, date_field_name=NOTICE_CREATED_AT)
        return notice_dict

    def _update_notice(self, notice: Notice, upsert: bool = False):
        self._write_lazy_fields(notice=notice)
        notice_dict = NoticeRepository._create_dict_from_notice(notice=notice)
        self.collection.update_one({MONGODB_COLLECTION_ID: notice_dict[MONGODB_COLLECTION_ID]},
                                   {"$set": notice_dict}, upsert=upsert)

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
            notice = self._create_notice_from_repository_result(result_dict)
            return notice
        return None

    def get_notices_by_status(self, notice_status: NoticeStatus) -> Iterator[Notice]:
        """
            This method provides all notices based on its status.
        :param notice_status:
        :return:
        """
        for result_dict in self.collection.find({NOTICE_STATUS: str(notice_status)}):
            notice = self._create_notice_from_repository_result(result_dict)
            yield notice

    def get_notice_ids_by_status(self, notice_status: NoticeStatus) -> Iterator[str]:
        """
            This method provides notice_ids based on notices status.
        :param notice_status:
        :return:
        """
        for result_dict in self.collection.find({NOTICE_STATUS: str(notice_status)}, {NOTICE_TED_ID: 1}):
            yield result_dict[NOTICE_TED_ID]

    def list(self) -> Iterator[Notice]:
        """
            This method allows all records to be retrieved from the repository.
        :return: list of notices
        """
        for result_dict in self.collection.find():
            notice = self._create_notice_from_repository_result(result_dict)
            yield notice
