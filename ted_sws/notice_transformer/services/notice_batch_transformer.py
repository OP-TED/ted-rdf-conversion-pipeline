from ted_sws.notice_transformer.adapters.notice_batch_transformer import MappingSuiteTransformationPool


def notice_batch_transformer(notice_id: str, mapping_transformation_pool: MappingSuiteTransformationPool) -> str:
    return mapping_transformation_pool.transform_notice_by_id(notice_id=notice_id)
