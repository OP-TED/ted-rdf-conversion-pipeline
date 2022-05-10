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


def get_unique_xpaths_from_notice_repository(mongodb_client: MongoClient) -> List[str]:
    """

    """
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    return notice_repository.collection.distinct("xml_metadata.unique_xpaths")


def get_unique_notice_id_from_notice_repository(mongodb_client: MongoClient) -> List[str]:
    """

    """
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    return notice_repository.collection.distinct("ted_id")


def get_minimal_set_of_xpaths_for_coverage_notices(notice_ids: List[str], mongodb_client: MongoClient) -> List[str]:
    """

    :param notice_ids:
    :return:
    """
    minimal_set_of_xpaths = []
    unique_notice_ids = notice_ids.copy()
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    while len(unique_notice_ids):
        tmp_result = list(notice_repository.collection.aggregate([
            {"$unwind": "$xml_metadata.unique_xpaths"},
            {"$match": {
                "xml_metadata.unique_xpaths": {"$nin": minimal_set_of_xpaths},
                "ted_id": {"$in": unique_notice_ids}
            }
            },
            {"$group": {"_id": "$xml_metadata.unique_xpaths", "count": {"$sum": 1},
                        "notice_ids": {"$push": "$ted_id"}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]))[0]
        minimal_set_of_xpaths.append(tmp_result["_id"])
        for notice_id in tmp_result["notice_ids"]:
            unique_notice_ids.remove(notice_id)

    return minimal_set_of_xpaths


def get_minimal_set_of_notices_for_coverage_xpaths(xpaths: List[str], mongodb_client: MongoClient) -> List[str]:
    minimal_set_of_notices = []
    unique_xpaths = xpaths.copy()
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    while len(unique_xpaths):
        tmp_result = list(notice_repository.collection.aggregate([
            {"$match": {
                "ted_id": {"$nin": minimal_set_of_notices},
            }
            },
            {"$unwind": "$xml_metadata.unique_xpaths"},
            {"$match": {
                "xml_metadata.unique_xpaths": {"$in": unique_xpaths},
            }
            },
            {"$group": {"_id": "$ted_id", "count": {"$sum": 1}, "xpaths": {"$push": "$xml_metadata.unique_xpaths"}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]))[0]
        minimal_set_of_notices.append(tmp_result["_id"])
        for xpath in tmp_result["xpaths"]:
            unique_xpaths.remove(xpath)

    return minimal_set_of_notices


def get_unique_notices_id_covered_by_xpaths(xpaths: List[str], mongodb_client: MongoClient) -> List[str]:
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    results = list(notice_repository.collection.aggregate([
        {"$match": {"xml_metadata.unique_xpaths": {"$in": xpaths}}},
        {
            "$group": {"_id": None,
                       "ted_ids": {"$push": "$ted_id"}
                       }
        },
        {
            "$project": {
                "_id": 0,
                "ted_ids": {
                    "$setUnion": {
                        "$reduce": {
                            "input": '$ted_ids',
                            "initialValue": [],
                            "in": {"$concatArrays": ['$$value', '$$this']}
                        }
                    }
                }
            }
        }
    ]))[0]["ted_ids"]
    return results


def get_unique_xpaths_covered_by_notices(notice_ids: List[str], mongodb_client: MongoClient) -> List[str]:
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    results = list(notice_repository.collection.aggregate([
        {"$match": {"ted_id": {"$in": notice_ids}}},
        {
            "$group": {"_id": None,
                       "xpaths": {"$push": "$xml_metadata.unique_xpaths"}
                       }
        },
        {
            "$project": {
                "_id": 0,
                "xpaths": {
                    "$setUnion": {
                        "$reduce": {
                            "input": '$xpaths',
                            "initialValue": [],
                            "in": {"$concatArrays": ['$$value', '$$this']}
                        }
                    }
                }
            }
        }
    ]))[0]["xpaths"]
    return results
