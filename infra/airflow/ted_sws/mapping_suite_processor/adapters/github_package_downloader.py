import abc
import pathlib
import shutil
import subprocess
import tempfile
from ted_sws import config

MAPPINGS_DIR_NAME = "mappings"


def get_repo_name_from_repo_url(repository_url: str) -> str:
    """
    This method will extract the name of the repository from a repository URL
    """
    url_path = pathlib.PurePosixPath(repository_url)
    return url_path.stem


class MappingSuitePackageDownloaderABC(abc.ABC):
    """
        This class is intended to download mapping_suite_package from external resources.
    """

    @abc.abstractmethod
    def download(self, output_mapping_suite_package_path: pathlib.Path):
        """
            This method downloads a mapping_suite_package and loads it at the output_mapping_suite_package_path provided.
        :param output_mapping_suite_package_path:
        :return:
        """


class GitHubMappingSuitePackageDownloader(MappingSuitePackageDownloaderABC):
    """
        This class downloads mapping_suite_package from GitHub.
    """

    def __init__(self, github_repository_url: str, branch_or_tag_name: str):
        """
        Option can be branch or tag, not both
        :param github_repository_url:
        :param branch_or_tag_name:
        """
        self.github_repository_url = github_repository_url
        self.branch_or_tag_name = branch_or_tag_name
        self.repository_name = get_repo_name_from_repo_url(repository_url=github_repository_url)

    def download(self, output_mapping_suite_package_path: pathlib.Path) -> str:
        """
            This method downloads a mapping_suite_package and loads it at the output_mapping_suite_package_path provided.
        :param output_mapping_suite_package_path:
        :return:
        """

        def get_git_head_hash(git_repository_path: pathlib.Path) -> str:
            """
                This function return hash for last commit with git.
            :return:
            """
            git_repository_path.mkdir(exist_ok=True, parents=True)
            result = subprocess.run(
                f'cd {git_repository_path} && git rev-parse {self.branch_or_tag_name}',
                shell=True,
                stdout=subprocess.PIPE)
            git_head_hash = result.stdout.decode(encoding="utf-8")
            return git_head_hash

        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_dir_path = pathlib.Path(tmp_dir)
            bash_script = f"cd {temp_dir_path} && git clone --branch {self.branch_or_tag_name} {self.github_repository_url}"
            subprocess.run(bash_script, shell=True,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.STDOUT)
            git_last_commit_hash = get_git_head_hash(
                git_repository_path=temp_dir_path / self.repository_name)
            downloaded_tmp_mapping_suite_path = temp_dir_path / self.repository_name / MAPPINGS_DIR_NAME
            shutil.copytree(downloaded_tmp_mapping_suite_path, output_mapping_suite_package_path, dirs_exist_ok=True)
        return git_last_commit_hash
