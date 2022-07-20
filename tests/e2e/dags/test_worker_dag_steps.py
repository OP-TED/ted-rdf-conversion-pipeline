from ted_sws import config
from ted_sws.core.model.notice import NoticeStatus, Notice
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from tests.e2e.dags import run_task, START_PROCESSING_NOTICE_TASK_ID, \
    NORMALISE_NOTICE_METADATA_TASK_ID, CHECK_ELIGIBILITY_FOR_TRANSFORMATION_TASK_ID, \
    PREPROCESS_XML_MANIFESTATION_TASK_ID, TRANSFORM_NOTICE_TASK_ID, RESOLVE_ENTITIES_IN_THE_RDF_MANIFESTATION_TASK_ID, \
    VALIDATE_TRANSFORMED_RDF_MANIFESTATION_TASK_ID, CHECK_ELIGIBILITY_FOR_PACKING_BY_VALIDATION_REPORT_TASK_ID, \
    GENERATE_METS_PACKAGE_TASK_ID, CHECK_PACKAGE_INTEGRITY_BY_PACKAGE_STRUCTURE_TASK_ID, \
    PUBLISH_NOTICE_IN_CELLAR_TASK_ID, CHECK_NOTICE_PUBLIC_AVAILABILITY_IN_CELLAR_TASK_ID, \
    CHECK_NOTICE_STATE_BEFORE_TRANSFORM_TASK_ID, CHECK_NOTICE_STATE_BEFORE_GENERATE_METS_PACKAGE_TASK_ID, \
    INDEX_NOTICE_XML_CONTENT_TASK_ID

DAG_ID = "worker_single_notice_process_orchestrator"


def execute_dag_step(dag, task_id: str, dag_config: dict, xcom_push_data: dict = None):
    assert dag.has_task(task_id)
    task = dag.get_task(task_id)
    assert task
    task_instance = run_task(dag, task, conf=dag_config, xcom_push_data=xcom_push_data)
    assert task_instance.state == "success"


def check_notice_status(notice_repository: NoticeRepository, notice_id: str, notice_status: NoticeStatus) -> Notice:
    notice = notice_repository.get(reference=notice_id)
    assert notice.status == notice_status
    return notice


def test_worker_dag_steps(dag_bag, notice_repository):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id=DAG_ID)
    assert dag is not None

    notice = next(notice_repository.get_notice_by_status(notice_status=NoticeStatus.RAW))
    notice_id = notice.ted_id
    dag_config = {"notice_id": notice_id, "notice_status": "RAW"}

    check_notice_status(notice_repository=notice_repository, notice_id=notice_id, notice_status=NoticeStatus.RAW)
    execute_dag_step(dag, task_id=START_PROCESSING_NOTICE_TASK_ID, dag_config=dag_config)
    execute_dag_step(dag, task_id=INDEX_NOTICE_XML_CONTENT_TASK_ID, dag_config=dag_config)
    notice = check_notice_status(notice_repository=notice_repository, notice_id=notice_id,
                                 notice_status=NoticeStatus.INDEXED)
    assert notice.xml_metadata is not None
    execute_dag_step(dag, task_id=NORMALISE_NOTICE_METADATA_TASK_ID, dag_config=dag_config)
    notice = check_notice_status(notice_repository=notice_repository, notice_id=notice_id,
                                 notice_status=NoticeStatus.NORMALISED_METADATA)
    assert notice.normalised_metadata is not None

    execute_dag_step(dag, task_id=CHECK_ELIGIBILITY_FOR_TRANSFORMATION_TASK_ID, dag_config=dag_config)
    check_notice_status(notice_repository=notice_repository, notice_id=notice_id,
                        notice_status=NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION)

    execute_dag_step(dag, task_id=CHECK_NOTICE_STATE_BEFORE_TRANSFORM_TASK_ID, dag_config=dag_config)

    execute_dag_step(dag, task_id=PREPROCESS_XML_MANIFESTATION_TASK_ID, dag_config=dag_config)
    notice = check_notice_status(notice_repository=notice_repository, notice_id=notice_id,
                                 notice_status=NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION)

    assert notice.rdf_manifestation is None

    execute_dag_step(dag, task_id=TRANSFORM_NOTICE_TASK_ID, dag_config=dag_config)
    notice = check_notice_status(notice_repository=notice_repository, notice_id=notice_id,
                                 notice_status=NoticeStatus.TRANSFORMED)

    assert notice.rdf_manifestation is not None
    assert notice.distilled_rdf_manifestation is None

    execute_dag_step(dag, task_id=RESOLVE_ENTITIES_IN_THE_RDF_MANIFESTATION_TASK_ID, dag_config=dag_config)
    notice = check_notice_status(notice_repository=notice_repository, notice_id=notice_id,
                                 notice_status=NoticeStatus.DISTILLED)

    assert notice.distilled_rdf_manifestation is not None

    execute_dag_step(dag, task_id=VALIDATE_TRANSFORMED_RDF_MANIFESTATION_TASK_ID, dag_config=dag_config)
    notice = check_notice_status(notice_repository=notice_repository, notice_id=notice_id,
                                 notice_status=NoticeStatus.VALIDATED)

    assert notice.rdf_manifestation.shacl_validations
    assert notice.rdf_manifestation.sparql_validations
    assert notice.distilled_rdf_manifestation.shacl_validations
    assert notice.distilled_rdf_manifestation.sparql_validations

    execute_dag_step(dag, task_id=CHECK_ELIGIBILITY_FOR_PACKING_BY_VALIDATION_REPORT_TASK_ID, dag_config=dag_config)
    check_notice_status(notice_repository=notice_repository, notice_id=notice_id,
                        notice_status=NoticeStatus.ELIGIBLE_FOR_PACKAGING)

    execute_dag_step(dag, task_id=CHECK_NOTICE_STATE_BEFORE_GENERATE_METS_PACKAGE_TASK_ID, dag_config=dag_config)

    assert notice.mets_manifestation is None

    execute_dag_step(dag, task_id=GENERATE_METS_PACKAGE_TASK_ID, dag_config=dag_config)
    notice = check_notice_status(notice_repository=notice_repository, notice_id=notice_id,
                                 notice_status=NoticeStatus.PACKAGED)

    assert notice.mets_manifestation is not None

    # TODO: add this steps when publish notice in cellar will work
    # execute_dag_step(dag, task_id=CHECK_PACKAGE_INTEGRITY_BY_PACKAGE_STRUCTURE_TASK_ID, xcom_push_data=XCOM_DEFAULT)
    # check_notice_status(notice_repository=notice_repository, notice_status=NoticeStatus.ELIGIBLE_FOR_PUBLISHING)
    #
    # execute_dag_step(dag, task_id=PUBLISH_NOTICE_IN_CELLAR_TASK_ID, xcom_push_data=XCOM_DEFAULT)
    # check_notice_status(notice_repository=notice_repository, notice_status=NoticeStatus.PUBLISHED)
    #
    # execute_dag_step(dag, task_id=CHECK_NOTICE_PUBLIC_AVAILABILITY_IN_CELLAR_TASK_ID, xcom_push_data=XCOM_DEFAULT)
    # check_notice_status(notice_repository=notice_repository, notice_status=NoticeStatus.PUBLICLY_AVAILABLE)

    notice_repository.mongodb_client.drop_database(config.MONGO_DB_AGGREGATES_DATABASE_NAME)
