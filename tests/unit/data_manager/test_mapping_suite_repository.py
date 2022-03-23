from deepdiff import DeepDiff

from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryMongoDB, \
    MappingSuiteRepositoryInFileSystem


def test_mapping_suite_repository_mongodb(mongodb_client, fake_mapping_suite):
    mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_suite_repository.add(mapping_suite=fake_mapping_suite)
    result_mapping_suite = mapping_suite_repository.get(reference=fake_mapping_suite.identifier)
    assert result_mapping_suite
    assert result_mapping_suite.identifier == fake_mapping_suite.identifier
    result_mapping_suite.title = "updated_title"
    mapping_suite_repository.update(mapping_suite=result_mapping_suite)
    result_mapping_suite = mapping_suite_repository.get(reference=fake_mapping_suite.identifier)
    assert result_mapping_suite.title ==  "updated_title"
    result_mapping_suites =list(mapping_suite_repository.list())
    assert len(result_mapping_suites) == 1
    mongodb_client.drop_database(MappingSuiteRepositoryMongoDB._database_name)


def test_mapping_suite_repository_mongodb_update_invalid_id(mongodb_client, fake_mapping_suite):
    mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_suite_repository.add(mapping_suite=fake_mapping_suite)
    result_mapping_suite = mapping_suite_repository.get(reference=fake_mapping_suite.identifier)
    assert result_mapping_suite
    assert result_mapping_suite.identifier == fake_mapping_suite.identifier
    result_mapping_suite.identifier = "updated_id"
    result_mapping_suite.title = "updated_title"
    mapping_suite_repository.update(mapping_suite=result_mapping_suite)
    result_mapping_suite = mapping_suite_repository.get(reference=result_mapping_suite.identifier)
    assert result_mapping_suite is None
    mongodb_client.drop_database(MappingSuiteRepositoryMongoDB._database_name)


def test_mapping_suite_repository_in_file_system(file_system_repository_path, fake_mapping_suite):
    mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=file_system_repository_path)
    mapping_suite_repository.clear_repository()
    mapping_suite_repository.add(mapping_suite=fake_mapping_suite)
    result_mapping_suite = mapping_suite_repository.get(reference=fake_mapping_suite.identifier)
    assert result_mapping_suite
    assert result_mapping_suite.identifier == fake_mapping_suite.identifier
    result_mapping_suite.title = "updated_title"
    mapping_suite_repository.update(mapping_suite=result_mapping_suite)
    result_mapping_suite = mapping_suite_repository.get(reference=fake_mapping_suite.identifier)
    assert result_mapping_suite.title ==  "updated_title"
    result_mapping_suites =list(mapping_suite_repository.list())
    assert len(result_mapping_suites) == 1
    result_mapping_suite.identifier = "new_id"
    mapping_suite_repository.add(mapping_suite=result_mapping_suite)
    result_mapping_suites = list(mapping_suite_repository.list())
    assert len(result_mapping_suites) == 2
    mapping_suite_repository.clear_repository()

def test_inter_transactions_mapping_suite_repositories(mongodb_client, file_system_repository_path, fake_mapping_suite):
    mapping_suite_repository_mongodb = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_suite_repository_file_system = MappingSuiteRepositoryInFileSystem(repository_path=file_system_repository_path)
    mapping_suite_repository_file_system.clear_repository()
    mapping_suite_repository_mongodb.add(mapping_suite=fake_mapping_suite)
    result_mapping_suite = mapping_suite_repository_mongodb.get(reference=fake_mapping_suite.identifier)
    mapping_suite_repository_file_system.add(mapping_suite=result_mapping_suite)
    result_mapping_suite = mapping_suite_repository_file_system.get(reference=fake_mapping_suite.identifier)
    assert DeepDiff(result_mapping_suite, fake_mapping_suite) == {}
    mapping_suite_repository_file_system.clear_repository()
    mongodb_client.drop_database(MappingSuiteRepositoryMongoDB._database_name)