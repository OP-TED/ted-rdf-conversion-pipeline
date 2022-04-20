import pathlib
from ted_sws import config
from ted_sws.mapping_suite_processor.adapters.github_package_downloader import GitHubMappingSuitePackageDownloader
from tests.e2e.mapping_suite_processor import MAPPING_SUITE_PACKAGE_NAME


def test_github_mapping_suite_package_downloader(tmpdir):
    mapping_suite_package_downloader = GitHubMappingSuitePackageDownloader(
        github_repository_url=config.GITHUB_TED_SWS_ARTEFACTS_URL)
    tmp_dir_path = pathlib.Path(tmpdir)
    mapping_suite_package_downloader.download(mapping_suite_package_name=MAPPING_SUITE_PACKAGE_NAME,
                                              output_mapping_suite_package_path=tmp_dir_path)
    mapping_suite_package_path = tmp_dir_path / MAPPING_SUITE_PACKAGE_NAME
    assert mapping_suite_package_path.is_dir()
