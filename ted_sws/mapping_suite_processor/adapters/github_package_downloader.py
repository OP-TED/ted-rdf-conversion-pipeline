import abc
import pathlib
import shutil
import subprocess
import tempfile


class MappingSuitePackageDownloaderABC(abc.ABC):
    """

    """

    @abc.abstractmethod
    def download(self, mapping_suite_package_name: str, output_mapping_suite_package_path: pathlib.Path):
        """

        :param mapping_suite_package_name:
        :param output_mapping_suite_package_path:
        :return:
        """


class GitHubMappingSuitePackageDownloader(MappingSuitePackageDownloaderABC):
    """

    """

    def __init__(self, github_repository_mappings_folder_url: str):
        """

        :param github_repository_mappings_folder_url:
        """
        self.github_repository_mappings_folder_url = github_repository_mappings_folder_url

    def download(self, mapping_suite_package_name: str, output_mapping_suite_package_path: pathlib.Path):
        """

        :param mapping_suite_package_name:
        :param output_mapping_suite_package_path:
        :return:
        """
        github_mapping_suite_package_url = f"{self.github_repository_mappings_folder_url}/{mapping_suite_package_name}"
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_dir_path = pathlib.Path(tmp_dir)
            bash_script = f"gitdir -d {temp_dir_path} {github_mapping_suite_package_url}"
            subprocess.run(bash_script, shell=True, stdout=subprocess.PIPE)
            downloaded_tmp_mapping_suite_path = temp_dir_path / "mappings" / mapping_suite_package_name
            shutil.copytree(downloaded_tmp_mapping_suite_path, output_mapping_suite_package_path, dirs_exist_ok=True)
