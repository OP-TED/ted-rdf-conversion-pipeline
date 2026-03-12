import json
import pathlib

from src.ted_sws import config
from src.ted_sws.mapping_suite_processor.adapters.github_ms_project_downloader import GitHubMappingSuiteDownloader, \
    get_repo_name_from_repo_url, MS_CONFIG_FILE_NAME, MS_CONFIG_DIR_NAME
from test.e2e.mapping_suite_processor import MAPPING_PACKAGE_NAME


def test_github_mapping_suite_downloader(tmpdir):
    mapping_suite_downloader = GitHubMappingSuiteDownloader(
        github_repository_url=config.GITHUB_TED_SWS_ARTEFACTS_URL, branch_or_tag_name="main")
    tmp_dir_path = pathlib.Path(tmpdir)
    mapping_suite_downloader.download(output_project_path=tmp_dir_path)
    mapping_package_path = tmp_dir_path / mapping_suite_downloader.MAPPINGS_DIR_NAME / MAPPING_PACKAGE_NAME
    assert mapping_package_path.is_dir()


def test_download_config_from_branch_copies_resource_files(tmpdir):
    """Test that download_config_from_branch copies both config and all referenced resource files."""
    mapping_suite_downloader = GitHubMappingSuiteDownloader(
        github_repository_url=config.GITHUB_TED_SWS_ARTEFACTS_URL, branch_or_tag_name="main")
    tmp_dir_path = pathlib.Path(tmpdir)

    # Download config from a specific branch
    config_branch = "config"
    mapping_suite_downloader.download_config_from_branch(
        output_project_path=tmp_dir_path, config_branch=config_branch)

    # Verify config file was copied
    config_file_path = tmp_dir_path / MS_CONFIG_DIR_NAME / MS_CONFIG_FILE_NAME
    assert config_file_path.is_file(), f"Config file should exist at {config_file_path}"

    # Parse config to get expected resource files
    with open(config_file_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    resource_refs = config_data.get('resource_references', {})
    file_paths = resource_refs.get('file_paths', [])

    assert len(file_paths) > 0, "Config should have resource_references.file_paths defined"

    # Verify all referenced resource files were copied
    missing_files = []
    for file_path in file_paths:
        relative_path = file_path.lstrip('/')
        resource_file = tmp_dir_path / relative_path
        if not resource_file.is_file():
            missing_files.append(relative_path)

    assert len(missing_files) == 0, f"Resource files not copied from branch '{config_branch}': {missing_files}"


def test_get_repo_name_from_repo_url():
    repo_url = "https://github.com/OP-TED/ted-rdf-mapping.git"
    repo_name = get_repo_name_from_repo_url(repository_url=repo_url)
    assert repo_name == "ted-rdf-mapping"
    assert isinstance(repo_name, str)
