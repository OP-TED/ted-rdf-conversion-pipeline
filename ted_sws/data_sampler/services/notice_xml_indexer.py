import pathlib
import re
import tempfile
import xml.etree.ElementTree as XMLElementTree
from io import StringIO
from typing import List, Set, Generator, Optional

from pymongo import MongoClient

from ted_sws.core.adapters.xml_preprocessor import XMLPreprocessor
from ted_sws.core.model.metadata import XMLMetadata
from ted_sws.core.model.notice import Notice
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.mapping_suite_processor.adapters.conceptual_mapping_reader import ConceptualMappingReader
from ted_sws.resources import XSLT_FILES_PATH

UNIQUE_XPATHS_XSLT_FILE_PATH = "get_unique_xpaths.xsl"
XSLT_PREFIX_RESULT = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"

INCLUDE_VALUES_BY_ATTRIBUTES_NAMES = {"schemeName", "unitCode", "listName"}
EXCLUDE_ATTRIBUTES_VALUES = {"nuts", "country", "cpv"}


def index_notice_by_id(notice_id: str, mongodb_client: MongoClient):
    """
        This function selects unique XPath from XMlManifestation from a notice and indexes notices with these unique XPath,
         where notice is selected based on notice_id.
    :param notice_id:
    :param mongodb_client:
    :return:
    """
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    notice = notice_repository.get(reference=notice_id)
    notice = index_notice(notice=notice)
    notice_repository.update(notice=notice)


def index_notice_xslt(notice: Notice, xslt_transformer=None) -> Notice:
    """
        This function selects unique XPath from XMlManifestation from a notice and indexes notices with these unique XPath.
    :param notice:
    :param xslt_transformer:
    :return:
    """

    with tempfile.NamedTemporaryFile() as fp:
        fp.write(notice.xml_manifestation.object_data.encode("utf-8"))
        xml_path = pathlib.Path(fp.name)
        xslt_path = XSLT_FILES_PATH
        xslt_path /= UNIQUE_XPATHS_XSLT_FILE_PATH

        if xslt_transformer is None:
            xslt_transformer = XMLPreprocessor()
        result = xslt_transformer.transform_with_xslt_to_string(xml_path=xml_path,
                                                                xslt_path=xslt_path)
        xpaths = result[len(XSLT_PREFIX_RESULT):].split(",")
        xml_metadata = XMLMetadata()
        xml_metadata.unique_xpaths = xpaths

        notice.set_xml_metadata(xml_metadata=xml_metadata)

    return notice


def get_all_xpath_generator(xml_content: str,
                            remove_namespaces: bool = True,
                            include_values_by_attribute_names: Optional[Set[str]] = None,
                            exclude_attribute_values: Optional[Set[str]] = None
                            ) -> Generator[str, None, None]:
    """
        Generate all XPaths based on the given XML content
    :param xml_content:
    :param remove_namespaces:
    :param include_values_by_attribute_names:
    :param exclude_attribute_values:
    return: generator of all XPaths based on the given XML content
    """
    xml_file = StringIO(xml_content)
    path = []
    it = XMLElementTree.iterparse(xml_file, events=('start', 'end'))
    for evt, el in it:
        if evt == 'start':
            if remove_namespaces:
                ns_tag = re.split('[{}]', el.tag, 2)[1:]
                path.append(ns_tag[1] if len(ns_tag) > 1 else el.tag)
            else:
                path.append(el.tag)
            xpath = "/" + '/'.join(path)
            for attribute_key, attribute_value in el.attrib.items():
                if (attribute_key in include_values_by_attribute_names) and (
                        attribute_value not in exclude_attribute_values):
                    yield f"{xpath}@{attribute_key}={attribute_value}"
                else:
                    yield f"{xpath}@{attribute_key}"
            yield xpath
        else:
            path.pop()


def index_eforms_notice(notice: Notice) -> Notice:
    xml_content = notice.xml_manifestation.object_data
    unique_xpaths = list(set(get_all_xpath_generator(xml_content=xml_content, remove_namespaces=True,
                                                     include_values_by_attribute_names=INCLUDE_VALUES_BY_ATTRIBUTES_NAMES,
                                                     exclude_attribute_values=EXCLUDE_ATTRIBUTES_VALUES
                                                     )))
    xml_metadata = XMLMetadata()
    xml_metadata.unique_xpaths = unique_xpaths
    notice.set_xml_metadata(xml_metadata=xml_metadata)
    return notice


def index_notice(notice: Notice, base_xpath="") -> Notice:
    # To be removed later if will not be used
    # def _notice_namespaces(xml_file) -> dict:
    #     _namespaces = dict([node for _, node in XMLElementTree.iterparse(xml_file, events=['start-ns'])])
    #     return {v: k for k, v in _namespaces.items()}

    def _ns_tag(ns_tag):
        tag = ns_tag[1]
        # Use just the tag, ignoring the namespace
        # ns = ns_tag[0]
        # if ns:
        #     ns_alias = namespaces[ns]
        #     if ns_alias:
        #         return ns_alias + ":" + tag
        return tag

    def _xpath_generator(xml_file):
        path = []
        it = XMLElementTree.iterparse(xml_file, events=('start', 'end'))
        for evt, el in it:
            if evt == 'start':
                ns_tag = re.split('[{}]', el.tag, 2)[1:]
                path.append(_ns_tag(ns_tag) if len(ns_tag) > 1 else el.tag)

                xpath = "/" + '/'.join(path)

                if xpath.startswith(ConceptualMappingReader.base_xpath_as_prefix(base_xpath)):
                    attributes = list(el.attrib.keys())
                    if len(attributes) > 0:
                        for attr in attributes:
                            yield xpath + "/@" + attr
                    yield xpath
            else:
                path.pop()

    with tempfile.NamedTemporaryFile() as fp:
        fp.write(notice.xml_manifestation.object_data.encode("utf-8"))

        # Not used for the moment (to be removed in the future if feature is not wanted back)
        # namespaces = _notice_namespaces(fp.name)
        xpaths = list(set(_xpath_generator(fp.name)))
        xml_metadata = XMLMetadata()
        xml_metadata.unique_xpaths = xpaths
        notice.set_xml_metadata(xml_metadata=xml_metadata)

    return notice


def get_unique_xpaths_from_notice_repository(mongodb_client: MongoClient) -> List[str]:
    """
        This function returns all unique XPaths in notice_repository.
    :param mongodb_client:
    :return:
    """
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    return notice_repository.xml_metadata_repository.collection.distinct("unique_xpaths")


def get_unique_notice_id_from_notice_repository(mongodb_client: MongoClient) -> List[str]:
    """
        This function returns all unique notice_id in notice_repository.
    :param mongodb_client:
    :return:
    """
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    return notice_repository.collection.distinct("ted_id")


def get_minimal_set_of_xpaths_for_coverage_notices(notice_ids: List[str], mongodb_client: MongoClient) -> List[str]:
    """
        This function returns the minimum set of XPaths covering the transmitted notices list.
    :param notice_ids:
    :param mongodb_client:
    :return:
    """
    minimal_set_of_xpaths = []
    unique_notice_ids = notice_ids.copy()
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    while len(unique_notice_ids):
        tmp_result = list(notice_repository.xml_metadata_repository.collection.aggregate([
            {"$match": {"metadata_type": {"$eq": "xml"}}},
            {"$unwind": "$unique_xpaths"},
            {"$match": {
                "unique_xpaths": {"$nin": minimal_set_of_xpaths},
                "ted_id": {"$in": unique_notice_ids}
            }
            },
            {"$group": {"_id": "$unique_xpaths", "count": {"$sum": 1},
                        "notice_ids": {"$push": "$ted_id"}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]))
        if tmp_result:
            tmp_result = tmp_result[0]
            minimal_set_of_xpaths.append(tmp_result["_id"])
            for notice_id in tmp_result["notice_ids"]:
                unique_notice_ids.remove(notice_id)

    return minimal_set_of_xpaths


def get_minimal_set_of_notices_for_coverage_xpaths(notice_ids: List[str], mongodb_client: MongoClient) -> List[str]:
    """
        This function returns the minimum set of notices that cover the list of transmitted XPaths.
    :param notice_ids:
    :param mongodb_client:
    :return:
    """
    minimal_set_of_notices = []
    unique_xpaths = get_unique_xpaths_covered_by_notices(notice_ids=notice_ids, mongodb_client=mongodb_client)
    search_notices = notice_ids.copy()
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    while len(unique_xpaths):
        tmp_result = list(notice_repository.xml_metadata_repository.collection.aggregate([
            {"$match": {
                "ted_id": {"$in": search_notices},
                "metadata_type": {"$eq": "xml"}
            }
            },
            {"$unwind": "$unique_xpaths"},
            {"$match": {
                "unique_xpaths": {"$in": unique_xpaths},
            }
            },
            {"$group": {"_id": "$ted_id", "count": {"$sum": 1}, "xpaths": {"$addToSet": "$unique_xpaths"}
                        }},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ], allowDiskUse=True))
        if tmp_result:
            tmp_result = tmp_result[0]
            search_notices.remove(tmp_result["_id"])
            minimal_set_of_notices.append(tmp_result["_id"])
            for xpath in tmp_result["xpaths"]:
                unique_xpaths.remove(xpath)

    return minimal_set_of_notices


def get_unique_notices_id_covered_by_xpaths(xpaths: List[str], mongodb_client: MongoClient) -> List[str]:
    """
        This function returns a list of notices that are covered by a list of XPaths.
    :param xpaths:
    :param mongodb_client:
    :return:
    """
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    results = list(notice_repository.xml_metadata_repository.collection.aggregate([
        {"$match": {"unique_xpaths": {"$in": xpaths},
                    "metadata_type": {"$eq": "xml"}
                    }
         },
        {
            "$group": {"_id": None,
                       "ted_ids": {"$push": "$ted_id"}
                       }
        }
    ]))
    return results[0]["ted_ids"] if results else results


def get_unique_xpaths_covered_by_notices(notice_ids: List[str], mongodb_client: MongoClient) -> List[str]:
    """
        This function returns a list of unique XPaths that are covered by the notices list.
    :param notice_ids:
    :param mongodb_client:
    :return:
    """
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    results = notice_repository.xml_metadata_repository.collection.aggregate([{"$match": {"ted_id": {"$in": notice_ids},
                                                                                          "metadata_type": {
                                                                                              "$eq": "xml"}
                                                                                          }
                                                                               }], allowDiskUse=True)
    unique_xpaths = set()
    for result in results:
        if result["unique_xpaths"] is not None:
            unique_xpaths.update(result["unique_xpaths"])
    return list(unique_xpaths)


def get_most_representative_notices(notice_ids: List[str], mongodb_client: MongoClient, top_k: int = None) -> List[str]:
    """
        This function returns top_k the most representative notices, from the list of notices provided.
    :param notice_ids:
    :param mongodb_client:
    :param top_k:
    :return:
    """
    minimal_set_of_notices = get_minimal_set_of_notices_for_coverage_xpaths(notice_ids=notice_ids,
                                                                            mongodb_client=mongodb_client)
    return minimal_set_of_notices[:top_k]
