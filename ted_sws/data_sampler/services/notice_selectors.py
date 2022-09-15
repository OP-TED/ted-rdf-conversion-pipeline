from typing import List

from pymongo import MongoClient

from ted_sws.data_manager.adapters.notice_repository import NoticeRepository

NOTICE_METADATA_FORM_NUMBER_FIELD_NAME = "form_number"
NOTICE_METADATA_EFORMS_SUBTYPE_FIELD_NAME = "eforms_subtype"


def get_notice_ids_by_normalised_metadata_field_value(field_name: str, field_value: str,
                                                      mongodb_client: MongoClient,
                                                      notice_filter: dict = None) -> List[str]:
    """
        This function returns a list of notice_ids, according to the value of a field in normalized_metadata.
    :param field_name:
    :param field_value:
    :param mongodb_client:
    :param notice_filter:
    :return:
    """
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    match_filter = {f"normalised_metadata.{field_name}": field_value, "xml_metadata": {"$ne": None}}
    if notice_filter:
        match_filter.update(notice_filter)
    notice_ids = list(notice_repository.collection.aggregate([
        {"$match": match_filter
         },
        {"$project": {"_id": 1, "ted_id": 1}}
        ,
        {
            "$group": {"_id": None,
                       "ted_ids": {"$push": "$ted_id"}
                       }
        }
    ], allowDiskUse=True))
    return notice_ids[0]["ted_ids"] if len(notice_ids) else notice_ids


def get_notice_ids_by_form_number(form_number: str, mongodb_client: MongoClient,
                                  notice_filter: dict = None) -> List[str]:
    """
        This function returns a list of notice_ids, according to a form_number.
    :param form_number:
    :param mongodb_client:
    :param notice_filter:
    :return:
    """
    return get_notice_ids_by_normalised_metadata_field_value(field_name=NOTICE_METADATA_FORM_NUMBER_FIELD_NAME,
                                                             field_value=form_number,
                                                             mongodb_client=mongodb_client,
                                                             notice_filter=notice_filter
                                                             )


def get_notice_ids_by_eforms_subtype(eforms_subtype: str, mongodb_client: MongoClient,
                                     notice_filter: dict = None) -> List[str]:
    """
        This function returns a list of notice_ids, according to an eforms_subtype.
    :param eforms_subtype:
    :param mongodb_client:
    :param notice_filter:
    :return:
    """
    return get_notice_ids_by_normalised_metadata_field_value(field_name=NOTICE_METADATA_EFORMS_SUBTYPE_FIELD_NAME,
                                                             field_value=eforms_subtype,
                                                             mongodb_client=mongodb_client,
                                                             notice_filter=notice_filter
                                                             )
