import pathlib
import tempfile
from typing import List

from pymongo import MongoClient

from ted_sws.core.adapters.xml_preprocessor import XMLPreprocessor
from ted_sws.core.model.metadata import XMLMetadata
from ted_sws.core.model.notice import Notice
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.resources import XSLT_FILES_PATH

UNIQUE_XPATHS_XSLT_FILE_PATH = "get_unique_xpaths.xsl"
XSLT_PREFIX_RESULT = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"


def index_notice_by_id(notice_id: str, mongodb_client: MongoClient):
    """

    :param notice_id:
    :param mongodb_client:
    :return:
    """
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice = notice_repository.get(reference=notice_id)
    notice = index_notice(notice=notice)
    notice_repository.update(notice=notice)


def index_notice(notice: Notice) -> Notice:
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


def get_unique_xpaths_from_notice_repository(mongodb_client: MongoClient) -> List:
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    return notice_repository.collection.distinct("xml_metadata.unique_xpaths")

def get_unique_notice_id_from_notice_repository(mongodb_client:MongoClient) -> List:
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    return notice_repository.collection.distinct("ted_id")

