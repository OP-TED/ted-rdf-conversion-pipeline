import logging
from typing import Iterator, Union
from pymongo import MongoClient

from ted_sws import config
from ted_sws.core.model.manifestation import XMLManifestation, RDFManifestation, METSManifestation
from ted_sws.core.model.metadata import NormalisedMetadata
from ted_sws.data_manager.adapters.repository_abc import NoticeRepositoryABC
from ted_sws.core.model.notice import Notice, NoticeStatus

logger = logging.getLogger(__name__)


class NoticeRepository(NoticeRepositoryABC):
    """
       This repository is intended for storing Notice objects.
    """

    _collection_name = "notice_collection"
    _database_name = config.MONGO_DB_AGGREGATES_DATABASE_NAME

    def __init__(self, mongodb_client: MongoClient, database_name: str = _database_name):
        mongodb_client = mongodb_client
        self._database_name = database_name
        notice_db = mongodb_client[self._database_name]
        self.collection = notice_db[self._collection_name]

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
            del notice_dict["_id"]
            notice = Notice(**notice_dict)
            notice._status = NoticeStatus[notice_dict["status"]]
            notice._normalised_metadata = init_object_from_dict(NormalisedMetadata, "normalised_metadata")
            notice._preprocessed_xml_manifestation = init_object_from_dict(XMLManifestation,
                                                                           "preprocessed_xml_manifestation")
            notice._distilled_rdf_manifestation = init_object_from_dict(RDFManifestation, "distilled_rdf_manifestation")
            notice._rdf_manifestation = init_object_from_dict(RDFManifestation, "rdf_manifestation")
            notice._mets_manifestation = init_object_from_dict(METSManifestation, "mets_manifestation")
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
        notice_dict["_id"] = notice_dict["ted_id"]
        notice_dict["status"] = str(notice_dict["status"])
        return notice_dict

    def add(self, notice: Notice):
        """
            This method allows you to add notice objects to the repository.
        :param notice:
        :return:
        """
        notice_dict = NoticeRepository._create_dict_from_notice(notice=notice)
        self.collection.update_one({'_id': notice_dict["_id"]}, {"$set": notice_dict}, upsert=True)

    def update(self, notice: Notice):
        """
            This method allows you to update notice objects to the repository
        :param notice:
        :return:
        """
        notice_dict = NoticeRepository._create_dict_from_notice(notice=notice)
        self.collection.update_one({'_id': notice_dict["_id"]}, {"$set": notice_dict})

    def get(self, reference) -> Notice:
        """
            This method allows a notice to be obtained based on an identification reference.
        :param reference:
        :return: Notice
        """
        result_dict = self.collection.find_one({"ted_id": reference})
        return NoticeRepository._create_notice_from_repository_result(result_dict)

    def get_notice_by_status(self, notice_status: NoticeStatus) -> Iterator[Notice]:
        """
            This method provides all notices based on its status.
        :param notice_status:
        :return:
        """
        for result_dict in self.collection.find({"status": str(notice_status)}):
            yield NoticeRepository._create_notice_from_repository_result(result_dict)

    def list(self) -> Iterator[Notice]:
        """
            This method allows all records to be retrieved from the repository.
        :return: list of notices
        """
        for result_dict in self.collection.find():
            yield NoticeRepository._create_notice_from_repository_result(result_dict)
