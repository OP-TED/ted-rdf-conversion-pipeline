from typing import List
from pymongo import MongoClient

from ted_sws.master_data_registry.services.entity_deduplication import deduplicate_procedure_entities

CET_URIS = ["http://www.w3.org/ns/org#Organization"]
PROCEDURE_CET_URI = "http://data.europa.eu/a4g/ontology#Procedure"


def notices_batch_distillation_pipeline(notice_ids: List[str], mongodb_client: MongoClient) -> List[str]:
    """

    :param notice_ids:
    :param mongodb_client:
    :return:
    """
    from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
    from ted_sws.master_data_registry.services.entity_deduplication import deduplicate_entities_by_cet_uri

    notices = []
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    for notice_id in notice_ids:
        notice = notice_repository.get(reference=notice_id)
        notice.set_distilled_rdf_manifestation(
            distilled_rdf_manifestation=notice.rdf_manifestation.model_copy())
        notices.append(notice)
    for cet_uri in CET_URIS:
        deduplicate_entities_by_cet_uri(notices=notices, cet_uri=cet_uri)
    deduplicate_procedure_entities(notices=notices, procedure_cet_uri=PROCEDURE_CET_URI, mongodb_client=mongodb_client)
    for notice in notices:
        notice_repository.update(notice=notice)
    return notice_ids


def notice_batch_transformer_pipeline(notice_ids: List[str], mongodb_client: MongoClient) -> List[str]:
    """

    :param notice_ids:
    :param mongodb_client:
    :return:
    """
    from ted_sws.notice_transformer.adapters.notice_batch_transformer import MappingSuiteTransformationPool
    from ted_sws.notice_transformer.services.notice_batch_transformer import notice_batch_transformer
    from concurrent.futures import ThreadPoolExecutor

    mapping_transformation_pool = MappingSuiteTransformationPool(mongodb_client=mongodb_client,
                                                                 transformation_timeout=300)
    result_notice_ids = []
    with ThreadPoolExecutor() as executor:
        features = [executor.submit(notice_batch_transformer, notice_id, mapping_transformation_pool) for notice_id in
                    notice_ids]
        for feature in features:
            result_notice_id = feature.result()
            if result_notice_id:
                result_notice_ids.append(result_notice_id)
    mapping_transformation_pool.close()
    return result_notice_ids
