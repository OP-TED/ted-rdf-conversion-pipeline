from dags.pipelines.notice_processor_pipelines import notice_normalisation_pipeline, notice_transformation_pipeline, \
    notice_validation_pipeline, notice_package_pipeline, notice_publish_pipeline
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.mapping_suite_processor.services.conceptual_mapping_processor import \
    mapping_suite_processor_from_github_expand_and_load_package_in_mongo_db

MAPPING_SUITE_PACKAGE_NAME = "package_F03_test"
MAPPING_SUITE_PACKAGE_ID = f"{MAPPING_SUITE_PACKAGE_NAME}_v2.3.0"


def test_notice_processor_pipelines(fake_mongodb_client):
    notice_ids = mapping_suite_processor_from_github_expand_and_load_package_in_mongo_db(
        mapping_suite_package_name=MAPPING_SUITE_PACKAGE_NAME,
        mongodb_client=fake_mongodb_client,
        load_test_data=True
    )
    notice_id = notice_ids[0]
    notice_repository = NoticeRepository(mongodb_client=fake_mongodb_client)
    notice = notice_repository.get(reference=notice_id)
    pipelines = [notice_normalisation_pipeline, notice_transformation_pipeline, notice_validation_pipeline,
                 notice_package_pipeline, notice_publish_pipeline]
    notice_states = [NoticeStatus.RAW, NoticeStatus.NORMALISED_METADATA, NoticeStatus.DISTILLED,
                     NoticeStatus.VALIDATED, NoticeStatus.PACKAGED, NoticeStatus.PUBLISHED]
    for index, pipeline in enumerate(pipelines):
        assert notice.status == notice_states[index]
        pipeline_output = pipeline(notice=notice, mongodb_client=fake_mongodb_client)
        assert pipeline_output.processed, f"{pipeline.__name__} not processed!"
        assert pipeline_output.store_result
        assert pipeline_output.notice
        notice = pipeline_output.notice
        assert notice.status == notice_states[index + 1]
