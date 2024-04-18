import pathlib
from ted_sws import config
from ted_sws.mapping_suite_processor.adapters.github_package_downloader import GitHubMappingSuitePackageDownloader, \
    get_repo_name_from_repo_url
from tests.e2e.mapping_suite_processor import MAPPING_SUITE_PACKAGE_NAME


def test_github_mapping_suite_package_downloader(tmpdir):
    mapping_suite_package_downloader = GitHubMappingSuitePackageDownloader(
        github_repository_url=config.GITHUB_TED_SWS_ARTEFACTS_URL, branch_or_tag_name="main")
    tmp_dir_path = pathlib.Path(tmpdir)
    mapping_suite_package_downloader.download(output_mapping_suite_package_path=tmp_dir_path)
    mapping_suite_package_path = tmp_dir_path / MAPPING_SUITE_PACKAGE_NAME
    assert mapping_suite_package_path.is_dir()


def test_get_repo_name_from_repo_url():
    repo_url = "https://github.com/OP-TED/ted-rdf-mapping.git"
    repo_name = get_repo_name_from_repo_url(repository_url=repo_url)
    assert repo_name == "ted-rdf-mapping"
    assert isinstance(repo_name, str)
