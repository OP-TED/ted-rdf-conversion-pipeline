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


def _test_dag_branch(dag, task_ids: list):
    for task_id in task_ids:
        assert dag.has_task(task_id)
    for index in range(0, len(task_ids) - 1):
        task_a = dag.get_task(task_ids[index])
        task_b = dag.get_task(task_ids[index + 1])
        assert task_b.task_id in set(map(lambda task: task.task_id, task_a.downstream_list))
        assert task_a.task_id in set(
            map(lambda task: task.task_id, task_b.upstream_list))


def test_transform_branch_worker_single_notice_process_orchestrator(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="worker_single_notice_process_orchestrator")
    assert dag is not None
    _test_dag_branch(dag, TRANSFORM_BRANCH_TASK_IDS)


def test_package_branch_worker_single_notice_process_orchestrator(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="worker_single_notice_process_orchestrator")
    assert dag is not None
    _test_dag_branch(dag, PACKAGE_BRANCH_TASK_IDS)


def test_publish_branch_worker_single_notice_process_orchestrator(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="worker_single_notice_process_orchestrator")
    assert dag is not None
    _test_dag_branch(dag, PUBLISH_BRANCH_TASK_IDS)


def test_full_branch_worker_single_notice_process_orchestrator(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="worker_single_notice_process_orchestrator")
    assert dag is not None
    _test_dag_branch(dag, FULL_BRANCH_TASK_IDS)


def test_worker_single_notice_process_orchestrator(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="worker_single_notice_process_orchestrator")
    assert dag is not None
