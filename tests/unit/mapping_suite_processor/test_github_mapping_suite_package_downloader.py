from ted_sws.mapping_suite_processor.adapters.github_package_downloader import GitHubMappingSuitePackageDownloader


def test_github_mapping_suite_downloader_with_credentials():
    result_github_url = "https://test_username:test_token@github.com/test_user/test_project.git"
    mapping_suite_package_downloader = GitHubMappingSuitePackageDownloader(
        github_repository_url="https://github.com/test_user/test_project.git", branch_or_tag_name="main",
        github_username="test_username", github_token="test_token")

    assert mapping_suite_package_downloader.github_repository_url == result_github_url
