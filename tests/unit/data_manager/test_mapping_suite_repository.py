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

def test_mapping_suite_repository_in_file_system(file_system_repository_path, fake_mapping_suite):
    mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=file_system_repository_path)
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