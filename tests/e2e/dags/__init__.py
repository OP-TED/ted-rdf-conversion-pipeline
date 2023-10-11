# from airflow.models import DagRun, TaskInstance
# from airflow.utils.types import DagRunType

INDEX_NOTICE_XML_CONTENT_TASK_ID = "index_notice_xml_content"
NORMALISE_NOTICE_METADATA_TASK_ID = "normalise_notice_metadata"
CHECK_ELIGIBILITY_FOR_TRANSFORMATION_TASK_ID = "check_eligibility_for_transformation"
PREPROCESS_XML_MANIFESTATION_TASK_ID = "preprocess_xml_manifestation"
TRANSFORM_NOTICE_TASK_ID = "transform_notice"
RESOLVE_ENTITIES_IN_THE_RDF_MANIFESTATION_TASK_ID = "resolve_entities_in_the_rdf_manifestation"
VALIDATE_TRANSFORMED_RDF_MANIFESTATION_TASK_ID = "validate_transformed_rdf_manifestation"
CHECK_ELIGIBILITY_FOR_PACKING_BY_VALIDATION_REPORT_TASK_ID = "check_eligibility_for_packing_by_validation_report"
GENERATE_METS_PACKAGE_TASK_ID = "generate_mets_package"
CHECK_PACKAGE_INTEGRITY_BY_PACKAGE_STRUCTURE_TASK_ID = "check_package_integrity_by_package_structure"
PUBLISH_NOTICE_IN_CELLAR_TASK_ID = "publish_notice_in_cellar"
CHECK_NOTICE_PUBLIC_AVAILABILITY_IN_CELLAR_TASK_ID = "check_notice_public_availability_in_cellar"
NOTICE_SUCCESSFULLY_PROCESSED_TASK_ID = "notice_successfully_processed"
FAIL_ON_STATE_TASK_ID = "fail_on_state"
CHECK_NOTICE_STATE_BEFORE_TRANSFORM_TASK_ID = "check_notice_state_before_transform"
CHECK_NOTICE_STATE_BEFORE_GENERATE_METS_PACKAGE_TASK_ID = "check_notice_state_before_generate_mets_package"
CHECK_NOTICE_STATE_BEFORE_PUBLISH_NOTICE_IN_CELLAR_TASK_ID = "check_notice_state_before_publish_notice_in_cellar"
CHECK_NOTICE_STATE_BEFORE_NOTICE_SUCCESSFULLY_PROCESSED_TASK_ID = "check_notice_state_before_notice_successfully_processed"
START_PROCESSING_NOTICE_TASK_ID = "start_processing_notice"

TRANSFORM_BRANCH_TASK_IDS = [
    CHECK_ELIGIBILITY_FOR_TRANSFORMATION_TASK_ID, CHECK_NOTICE_STATE_BEFORE_TRANSFORM_TASK_ID,
    PREPROCESS_XML_MANIFESTATION_TASK_ID, TRANSFORM_NOTICE_TASK_ID,
    RESOLVE_ENTITIES_IN_THE_RDF_MANIFESTATION_TASK_ID,
    VALIDATE_TRANSFORMED_RDF_MANIFESTATION_TASK_ID,
    CHECK_ELIGIBILITY_FOR_PACKING_BY_VALIDATION_REPORT_TASK_ID,
    CHECK_NOTICE_STATE_BEFORE_GENERATE_METS_PACKAGE_TASK_ID
]

PACKAGE_BRANCH_TASK_IDS = [
    GENERATE_METS_PACKAGE_TASK_ID, CHECK_PACKAGE_INTEGRITY_BY_PACKAGE_STRUCTURE_TASK_ID,
    CHECK_NOTICE_STATE_BEFORE_PUBLISH_NOTICE_IN_CELLAR_TASK_ID
]

PUBLISH_BRANCH_TASK_IDS = [
    PUBLISH_NOTICE_IN_CELLAR_TASK_ID, CHECK_NOTICE_PUBLIC_AVAILABILITY_IN_CELLAR_TASK_ID,
    CHECK_NOTICE_STATE_BEFORE_NOTICE_SUCCESSFULLY_PROCESSED_TASK_ID,
    NOTICE_SUCCESSFULLY_PROCESSED_TASK_ID
]

FULL_BRANCH_TASK_IDS = [START_PROCESSING_NOTICE_TASK_ID,
                        NORMALISE_NOTICE_METADATA_TASK_ID] + TRANSFORM_BRANCH_TASK_IDS + PACKAGE_BRANCH_TASK_IDS + PUBLISH_BRANCH_TASK_IDS

#
# def run_task(dag, task, conf: dict, xcom_push_data: dict = None, ignore_first_depends_on_past=True) -> TaskInstance:
#     start_date = dag.default_args["start_date"]
#     end_date = dag.default_args["start_date"]
#     start_date = start_date or task.start_date
#     end_date = end_date or task.end_date or timezone.utcnow()
#
#     info = list(task.dag.iter_dagrun_infos_between(start_date, end_date, align=False))[0]
#     ignore_depends_on_past = info.logical_date == start_date and ignore_first_depends_on_past
#     dr = DagRun(
#         dag_id=task.dag_id,
#         run_id=DagRun.generate_run_id(DagRunType.MANUAL, info.logical_date),
#         run_type=DagRunType.MANUAL,
#         execution_date=info.logical_date,
#         data_interval=info.data_interval,
#         conf=conf
#     )
#     ti = TaskInstance(task, run_id=None)
#     ti.dag_run = dr
#
#     if xcom_push_data is not None:
#         for key, value in xcom_push_data.items():
#             ti.xcom_push(key=str(key), value=value)
#
#     ti.run(
#         mark_success=False,
#         ignore_task_deps=True,
#         ignore_depends_on_past=ignore_depends_on_past,
#         ignore_ti_state=False,
#         test_mode=True,
#     )
#     return ti
