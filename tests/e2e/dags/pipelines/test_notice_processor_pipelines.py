from dags.pipelines.notice_processor_pipelines import notice_normalisation_pipeline, notice_transformation_pipeline
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

    normalisation_pipeline_output = notice_normalisation_pipeline(notice=notice,
                                                                  mongodb_client=fake_mongodb_client)
    assert normalisation_pipeline_output.processed
    assert normalisation_pipeline_output.store_result
    assert normalisation_pipeline_output.notice
    normalised_notice = normalisation_pipeline_output.notice

    transformation_pipeline_output = notice_transformation_pipeline(notice=normalised_notice,
                                                                    mongodb_client=fake_mongodb_client)
    assert transformation_pipeline_output.processed
    assert transformation_pipeline_output.store_result
    assert transformation_pipeline_output.notice
    transformed_notice = transformation_pipeline_output.notice

    print(transformed_notice.normalised_metadata.form_number)
    print(transformed_notice.status)
