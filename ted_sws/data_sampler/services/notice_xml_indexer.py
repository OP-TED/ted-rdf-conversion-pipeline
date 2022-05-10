import pathlib
import tempfile
from typing import List, Iterator

from pymongo import MongoClient
from pymongo.command_cursor import CommandCursor

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
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    return notice_repository.collection.distinct("xml_metadata.unique_xpaths")


def get_unique_notice_id_from_notice_repository(mongodb_client: MongoClient) -> Iterator:
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    return notice_repository.collection.distinct("ted_id")


def get_minimal_set_of_xpaths_for_coverage_notices(notice_ids: List[str]) -> List[str]:
    minimal_set_of_xpaths = []
    covered_notice_ids = []
    while len(notice_ids):
        xpaths = []
        for xpath_id in list(unique_xpaths):
            tmp_result = list(
                objects_collection.aggregate([{"$match": {"xpath": {"$in": [xpath_id]},
                                                          "notices": {"$in": unique_notice_ids}}},
                                              {"$project": {"_id": 0,
                                                            "notice_id": "$notices"}},
                                              {

                                                  "$group": {"_id": None,
                                                             "notice_ids": {"$push": "$notice_id"}
                                                             }
                                              },
                                              {"$project": {"_id": 0,
                                                            "notice_ids": 1,
                                                            "count_notices": {"$size": "$notice_ids"}}},
                                              {
                                                  "$addFields": {"xpath": xpath_id}
                                              }
                                              ]))

            if len(tmp_result):
                xpaths.append(tmp_result[0])

        # for xpath in xpaths:
        #  print(xpath)
        top_xpath = sorted(xpaths, key=lambda d: d['count_notices'], reverse=True)[0]
        minimal_set_of_xpaths.append(top_xpath["xpath"])
        notice_ids = top_xpath["notice_ids"]
        for notice_id in notice_ids:
            unique_notice_ids.remove(notice_id)
            covered_notice_ids.append(notice_id)

    print("minimal_set_of_xpaths: ", minimal_set_of_xpaths)


def get_minimal_set_of_notices_for_coverage_xpaths(xpaths: List[str], mongodb_client: MongoClient) -> List[str]:
    minimal_set_of_notices = []
    unique_xpaths = xpaths.copy()
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    while len(unique_xpaths):
        tmp_result = notice_repository.collection.aggregate([
            {"$match": {
                "ted_id": {"$nin": minimal_set_of_notices},
            }
            },
            {"$unwind": "$xml_metadata.unique_xpaths"},
            {"$match": {
                "xml_metadata.unique_xpaths": {"$in": unique_xpaths},
            }
            },
            {"$group": {"_id": "$ted_id", "count": {"$sum": 1}, "xpaths": {"$push" : "$xml_metadata.unique_xpaths"}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ])
        minimal_set_of_notices.append(tmp_result["_id"])
        for xpath in tmp_result["xpaths"]:
            unique_xpaths.remove(xpath)



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
