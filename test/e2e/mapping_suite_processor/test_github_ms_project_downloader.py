import pathlib

from src.ted_sws import config
from src.ted_sws.mapping_suite_processor.adapters.github_ms_project_downloader import GitHubMappingSuiteDownloader, \
    get_repo_name_from_repo_url
from test.e2e.mapping_suite_processor import MAPPING_PACKAGE_NAME


def test_github_mapping_suite_downloader(tmpdir):
    mapping_suite_downloader = GitHubMappingSuiteDownloader(
        github_repository_url=config.GITHUB_TED_SWS_ARTEFACTS_URL, branch_or_tag_name="main")
    tmp_dir_path = pathlib.Path(tmpdir)
    mapping_suite_downloader.download(output_project_path=tmp_dir_path)
    mapping_package_path = tmp_dir_path / mapping_suite_downloader.MAPPINGS_DIR_NAME / MAPPING_PACKAGE_NAME
    assert mapping_package_path.is_dir()


def test_get_repo_name_from_repo_url():
    repo_url = "https://github.com/OP-TED/ted-rdf-mapping.git"
    repo_name = get_repo_name_from_repo_url(repository_url=repo_url)
    assert repo_name == "ted-rdf-mapping"
    assert isinstance(repo_name, str)
