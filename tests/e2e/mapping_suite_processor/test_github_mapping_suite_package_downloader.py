import pathlib
import shutil
import subprocess
import tempfile

from ted_sws import config
from ted_sws.mapping_suite_processor.adapters.github_package_downloader import GitHubMappingSuitePackageDownloader

MAPPING_SUITE_PACKAGE_NAME = "package_F03"


def test_github_mapping_suite_package_downloader():
    mapping_suite_package_downloader = GitHubMappingSuitePackageDownloader(
        github_repository_mappings_folder_url=config.GITHUB_MAPPINGS_URL)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir_path = pathlib.Path(tmp_dir)
        mapping_suite_package_downloader.download(mapping_suite_package_name=MAPPING_SUITE_PACKAGE_NAME,
                                                  output_mapping_suite_package_path=tmp_dir_path)
        mapping_suite_package_path = tmp_dir_path / MAPPING_SUITE_PACKAGE_NAME
        assert mapping_suite_package_path.is_dir()


def test_dummy():
    mapping_suite_package_name = MAPPING_SUITE_PACKAGE_NAME
    github_mapping_suite_package_url = f"{config.GITHUB_MAPPINGS_URL}/{mapping_suite_package_name}"
    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_dir_path = pathlib.Path(tmp_dir)
        bash_script = f"python3 -m gitdir -d {temp_dir_path} {github_mapping_suite_package_url}"
        subprocess.run(bash_script, shell=True, stdout=subprocess.PIPE)
        print(list(temp_dir_path.iterdir()))
        # downloaded_tmp_mapping_suite_path = temp_dir_path / "mappings" / mapping_suite_package_name
        # shutil.copytree(downloaded_tmp_mapping_suite_path, output_mapping_suite_package_path, dirs_exist_ok=True)
