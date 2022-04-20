import abc
import pathlib
import shutil
import subprocess
import tempfile

GITHUB_TED_SWS_ARTEFACTS_MAPPINGS_PATH = "ted-sws-artefacts/mappings"


class MappingSuitePackageDownloaderABC(abc.ABC):
    """
        This class is intended to download mapping_suite_package from external resources.
    """

    @abc.abstractmethod
    def download(self, mapping_suite_package_name: str, output_mapping_suite_package_path: pathlib.Path):
        """
            This method downloads a mapping_suite_package and loads it at the output_mapping_suite_package_path provided.
        :param mapping_suite_package_name:
        :param output_mapping_suite_package_path:
        :return:
        """


class GitHubMappingSuitePackageDownloader(MappingSuitePackageDownloaderABC):
    """
        This class downloads mapping_suite_package from GitHub.
    """

    def __init__(self, github_repository_url: str):
        """

        :param github_repository_url:
        """
        self.github_repository_url = github_repository_url

    def download(self, mapping_suite_package_name: str, output_mapping_suite_package_path: pathlib.Path):
        """
            This method downloads a mapping_suite_package and loads it at the output_mapping_suite_package_path provided.
        :param mapping_suite_package_name:
        :param output_mapping_suite_package_path:
        :return:
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_dir_path = pathlib.Path(tmp_dir)
            bash_script = f"cd {temp_dir_path} && git clone {self.github_repository_url}"
            subprocess.run(bash_script, shell=True,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.STDOUT)
            downloaded_tmp_mapping_suite_path = temp_dir_path / GITHUB_TED_SWS_ARTEFACTS_MAPPINGS_PATH / mapping_suite_package_name
            mapping_suite_package_path = output_mapping_suite_package_path / mapping_suite_package_name
            shutil.copytree(downloaded_tmp_mapping_suite_path, mapping_suite_package_path, dirs_exist_ok=True)
