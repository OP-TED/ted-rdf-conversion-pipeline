from src.dags.load_mapping_package_in_database import \
    FETCH_MAPPING_PACKAGE_FROM_GITHUB_INTO_MONGODB, MAPPING_PACKAGE_NAME_DAG_PARAM_KEY
from src.ted_sws import config
from src.ted_sws.data_manager.adapters.mapping_package_repository import MappingPackageRepositoryMongoDB
from test.e2e.dags import run_task


def test_loading_mapping_package_in_mongodb(dag_bag, mongodb_client, mapping_package_id, mapping_package_id_with_version):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="load_mapping_package_in_mongodb")
    worker_dag = dag_bag.get_dag(dag_id="worker_single_notice_process_orchestrator")
    assert dag is not None
    assert worker_dag is not None
    assert dag.has_task(FETCH_MAPPING_PACKAGE_FROM_GITHUB_INTO_MONGODB)
    fetch_step = dag.get_task(FETCH_MAPPING_PACKAGE_FROM_GITHUB_INTO_MONGODB)
    assert fetch_step
    mapping_package_repository = MappingPackageRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_package = mapping_package_repository.get(reference=mapping_package_id_with_version)
    assert mapping_package is None
    task_instance = run_task(dag=dag, task=fetch_step,
                             conf={MAPPING_PACKAGE_NAME_DAG_PARAM_KEY: mapping_package_id, "load_test_data": True})
    mapping_package = mapping_package_repository.get(reference=mapping_package_id_with_version)
    assert mapping_package is not None
    assert task_instance.state == "success"
    mongodb_client.drop_database(config.MONGO_DB_AGGREGATES_DATABASE_NAME)
