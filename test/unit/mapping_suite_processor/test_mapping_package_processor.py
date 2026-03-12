import shutil
from unittest.mock import Mock, patch

import pytest

from src.ted_sws.data_manager.adapters.mapping_package_repository import MappingPackageRepositoryInFileSystem, \
    MappingPackageRepositoryMongoDB
from src.ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryMongoDB
from src.ted_sws.mapping_suite_processor.services.mapping_package_processor import \
    load_mapping_suite_and_packages_from_github_to_mongo_db, mapping_package_processor_load_package_in_mongo_db
from src.ted_sws.mapping_suite_processor.services import MappingPackageProcessorServiceError
from test import TEST_DATA_PATH, temporary_copy


def test_mapping_package_processor_upload_in_mongodb(file_system_repository_path, mongodb_client,
                                                   test_package_identifier, aggregates_database_name):
    with temporary_copy(file_system_repository_path) as tmp_mapping_package_path:
        mapping_package_path = tmp_mapping_package_path / "test_package"
        mapping_package_repository = MappingPackageRepositoryInFileSystem(
            repository_path=tmp_mapping_package_path)
        mapping_package = mapping_package_repository.get(reference=mapping_package_path.name)
        mapping_package_processor_load_package_in_mongo_db(package=mapping_package,
                                                         mongodb_client=mongodb_client)
        mapping_package_repository = MappingPackageRepositoryInFileSystem(
            repository_path=tmp_mapping_package_path)
        mapping_package = mapping_package_repository.get(reference=mapping_package_path.name)
        assert mapping_package
        mapping_package_repository = MappingPackageRepositoryMongoDB(mongodb_client=mongodb_client)
        mapping_package = mapping_package_repository.get(reference=test_package_identifier)
        assert mapping_package

    mongodb_client.drop_database(aggregates_database_name)


def test_load_mapping_suite_config_from_github_to_mongo_db(mongodb_client, aggregates_database_name):
    test_suite_path = TEST_DATA_PATH / "mapping_suite_processor" / "mapping_project_eforms"

    mock_downloader = Mock()
    mock_downloader.MAPPINGS_DIR_NAME = "mappings"
    mock_downloader.MS_CONFIG_DIR_NAME = "config"
    mock_downloader.MS_CONFIG_FILE_NAME = "mapping_suite_config.json"

    def fake_download(output_project_path):
        """Copy test suite config into output path and create empty mappings dir."""

        # Create config directory and copy config file
        config_dir = output_project_path / "config"
        config_dir.mkdir(parents=True, exist_ok=True)

        src_config = test_suite_path / "config" / "mapping_suite_config.json"
        if src_config.exists():
            shutil.copy2(src_config, config_dir / "mapping_suite_config.json")

        # Create empty mappings directory (required by processor)
        mappings_dir = output_project_path / "mappings"
        mappings_dir.mkdir(parents=True, exist_ok=True)

        return "fake-commit-hash-123"

    mock_downloader.download.side_effect = fake_download

    with patch('src.ted_sws.mapping_suite_processor.services.mapping_package_processor.GitHubMappingSuiteDownloader',
               return_value=mock_downloader):
        load_mapping_suite_and_packages_from_github_to_mongo_db(
            mapping_package_name=None,
            mongodb_client=mongodb_client,
            load_test_data=False
        )

    # Verify mapping suite config was loaded
    mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    suites = list(mapping_suite_repository.list())

    assert len(suites) > 0, "Mapping suite config should be loaded"
    assert suites[0].id is not None, "Mapping suite should have valid id"
    assert suites[0].mapping_suite_config is not None, "Mapping suite config should be present"

    mongodb_client.drop_database(aggregates_database_name)


def test_load_mapping_suite_config_directory_missing_file(mongodb_client, aggregates_database_name):
    mock_downloader = Mock()
    mock_downloader.MAPPINGS_DIR_NAME = "mappings"
    mock_downloader.MS_CONFIG_DIR_NAME = "config"
    mock_downloader.MS_CONFIG_FILE_NAME = "mapping_suite_config.json"

    def fake_download(output_project_path):
        """Create config dir but don't put the file in it."""
        config_dir = output_project_path / "config"
        config_dir.mkdir(parents=True, exist_ok=True)

        mappings_dir = output_project_path / "mappings"
        mappings_dir.mkdir(parents=True, exist_ok=True)

        return "fake-commit-hash-123"

    mock_downloader.download.side_effect = fake_download

    with patch('src.ted_sws.mapping_suite_processor.services.mapping_package_processor.GitHubMappingSuiteDownloader',
               return_value=mock_downloader):
        with pytest.raises(MappingPackageProcessorServiceError) as exc_info:
            load_mapping_suite_and_packages_from_github_to_mongo_db(
                mapping_package_name=None,
                mongodb_client=mongodb_client,
                load_test_data=False
            )

    assert "MISSING config file" in str(exc_info.value)

    mongodb_client.drop_database(aggregates_database_name)


def test_msconfig_branch_calls_download_config_from_branch(mongodb_client, aggregates_database_name):
    """Test that msconfig_branch parameter triggers download_config_from_branch and uses that config."""
    test_suite_path = TEST_DATA_PATH / "mapping_suite_processor" / "mapping_project_eforms"

    mock_downloader = Mock()
    mock_downloader.MAPPINGS_DIR_NAME = "mappings"
    mock_downloader.MS_CONFIG_DIR_NAME = "config"
    mock_downloader.MS_CONFIG_FILE_NAME = "mapping_suite_config.json"

    def fake_download(output_project_path):
        """Simulate downloading packages branch - NO config provided here."""
        # Create empty mappings directory only (no config)
        mappings_dir = output_project_path / "mappings"
        mappings_dir.mkdir(parents=True, exist_ok=True)
        return "fake-commit-hash-456"

    def fake_download_config_from_branch(output_project_path, config_branch):
        """Simulate downloading config from separate branch."""
        config_dir = output_project_path / "config"
        config_dir.mkdir(parents=True, exist_ok=True)

        src_config = test_suite_path / "config" / "mapping_suite_config.json"
        if src_config.exists():
            shutil.copy2(src_config, config_dir / "mapping_suite_config.json")

    mock_downloader.download.side_effect = fake_download
    mock_downloader.download_config_from_branch.side_effect = fake_download_config_from_branch

    with patch('src.ted_sws.mapping_suite_processor.services.mapping_package_processor.GitHubMappingSuiteDownloader',
               return_value=mock_downloader):
        load_mapping_suite_and_packages_from_github_to_mongo_db(
            mapping_package_name=None,
            mongodb_client=mongodb_client,
            load_test_data=False,
            msconfig_branch="config-branch"
        )

    # Verify download_config_from_branch was called with correct branch
    mock_downloader.download_config_from_branch.assert_called_once()
    call_args = mock_downloader.download_config_from_branch.call_args
    assert call_args.kwargs['config_branch'] == "config-branch"

    # Verify mapping suite config was loaded (proving config from branch was used)
    mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    suites = list(mapping_suite_repository.list())

    assert len(suites) > 0, "Mapping suite config from msconfig_branch should be loaded"
    assert suites[0].id is not None, "Mapping suite should have valid id"

    mongodb_client.drop_database(aggregates_database_name)
