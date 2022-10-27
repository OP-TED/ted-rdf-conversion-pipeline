from typing import List

from pymongo import MongoClient

from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.master_data_registry.services.entity_deduplication import deduplicate_entities_by_cet_uri

CET_URIS = ["http://www.w3.org/ns/org#Organization"]


def notices_batch_distillation_pipeline(notice_ids: List[str], mongodb_client: MongoClient) -> List[str]:
    """

    :param notice_ids:
    :param mongodb_client:
    :return:
    """
    notices = []
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    for notice_id in notice_ids:
        notice = notice_repository.get(reference=notice_id)
        notice.set_distilled_rdf_manifestation(
            distilled_rdf_manifestation=notice.rdf_manifestation.copy())
        notices.append(notice)
    for cet_uri in CET_URIS:
        deduplicate_entities_by_cet_uri(notices=notices, cet_uri=cet_uri)
    for notice in notices:
        notice_repository.update(notice=notice)
    return notice_ids
