import abc
import pathlib
import tempfile
from typing import List, Optional

from pymongo import MongoClient

from ted_sws import config
from ted_sws.core.adapters.xml_preprocessor import XMLPreprocessor
from ted_sws.core.model.metadata import XMLMetadata, XPathMetadata
from ted_sws.core.model.notice import Notice
from ted_sws.resources import XSLT_FILES_PATH

UNIQUE_XPATHS_XSLT_FILE_PATH = "get_unique_xpaths.xsl"
XSLT_PREFIX_RESULT = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"


class NoticeXMLIndexerABC(abc.ABC):
    """

    """

    @abc.abstractmethod
    def index_notice(self, notice: Notice):
        """

        :param notice:
        :return:
        """


class NoticeXMLIndexer(NoticeXMLIndexerABC):
    """

    """
    _collection_name = "notice_xpaths_index"
    _database_name = config.MONGO_DB_AGGREGATES_DATABASE_NAME

    def __init__(self, mongodb_client: MongoClient, database_name: str = _database_name):
        self.mongodb_client = mongodb_client
        notice_xpaths_index_db = mongodb_client[self._database_name]
        self.collection = notice_xpaths_index_db[self._collection_name]

    @staticmethod
    def _create_xpath_metadata_from_dict(xpath_metadata_dict: dict) -> Optional[XPathMetadata]:
        """

        :param xpath_metadata_dict:
        :return:
        """
        if xpath_metadata_dict:
            del xpath_metadata_dict["_id"]

        return None

    @staticmethod
    def _create_dict_from_xpath_metadata(xpath_metadata: XPathMetadata) -> dict:
        """

        :param self:
        :param xpath_metadata:
        :return:
        """
        xpath_metadata_dict = xpath_metadata.dict()
        xpath_metadata_dict["_id"] = xpath_metadata.xpath
        return xpath_metadata_dict

    def register_inverse_index(self, notice_id: str, xpath: str):
        """

        :param notice_id:
        :param xpath:
        :return:
        """
        result_dict = self.collection.find_one({"xpath": xpath})
        #if result_dict:



    def index_notice(self, notice: Notice) -> Notice:
        """

        :param notice:
        :return:
        """
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(notice.xml_manifestation.object_data.encode("utf-8"))
            xml_path = pathlib.Path(fp.name)
            xslt_path = XSLT_FILES_PATH / UNIQUE_XPATHS_XSLT_FILE_PATH
            xslt_transformer = XMLPreprocessor()
            result = xslt_transformer.transform_with_xslt_to_string(xml_path=xml_path,
                                                                    xslt_path=xslt_path)
            unique_xpaths = result[len(XSLT_PREFIX_RESULT):].split(",")
            notice.xml_metadata = XMLMetadata(unique_xpaths=unique_xpaths)

        return notice
