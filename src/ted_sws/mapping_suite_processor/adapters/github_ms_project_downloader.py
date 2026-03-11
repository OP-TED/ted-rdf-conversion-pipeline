import abc
import pathlib
import shutil
import subprocess
import tempfile
from typing import ClassVar
from src.ted_sws import config
from src.ted_sws.event_manager.services.log import log_technical_info
# TODO: get from env or config
MAPPINGS_DIR_NAME = "mappings"
MS_CONFIG_DIR_NAME = "config"
MS_CONFIG_FILE_NAME = "mapping_suite_config.json"


def get_repo_name_from_repo_url(repository_url: str) -> str:
    """
    This method will extract the name of the repository from a repository URL
    """
    url_path = pathlib.PurePosixPath(repository_url)
    return url_path.stem


class MappingSuiteDownloaderABC(abc.ABC):
    """
    This class is intended to download a mapping suite (project) from an external resources.
    """
    MAPPINGS_DIR_NAME: ClassVar[str] = "mappings"
    MS_CONFIG_DIR_NAME: ClassVar[str] = "config"
    MS_CONFIG_FILE_NAME: ClassVar[str] = "mapping_suite_config.json"

    @abc.abstractmethod
    def download(self, output_project_path: pathlib.Path):
        """
        This method downloads a mapping suite and places it at the output_project_path provided.
        :param output_project_path:
        :return:
        """


class GitHubMappingSuiteDownloader(MappingSuiteDownloaderABC):
    """
    This class downloads a mapping suite (project) from GitHub.
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
        self.mappings_dir_name = MAPPINGS_DIR_NAME
        self.config_dir_name = MS_CONFIG_DIR_NAME

    def download_config_from_branch(self, output_project_path: pathlib.Path, config_branch: str) -> None:
        """
        Downloads only the config directory from a specific branch and places it at output_project_path/config.
        :param output_project_path: The destination path where the config directory will be placed
        :param config_branch: The branch name to fetch the config from
        :return: None
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_dir_path = pathlib.Path(tmp_dir)
            bash_script = f"cd {temp_dir_path} && git clone --branch {config_branch} --depth 1 {self.github_repository_url}"
            subprocess.run(bash_script, shell=True,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.STDOUT)
            downloaded_tmp_project_path = temp_dir_path / self.repository_name
            source_config_path = downloaded_tmp_project_path / self.config_dir_name
            dest_config_path = output_project_path / self.config_dir_name
            if source_config_path.is_dir():
                shutil.copytree(source_config_path, dest_config_path, dirs_exist_ok=True)

    def download(self, output_project_path: pathlib.Path) -> str:
        """
        This method downloads a mapping suite and places it at the output_project_path provided.
        :param output_project_path:
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
            return (git_head_hash or "").strip()

        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_dir_path = pathlib.Path(tmp_dir)
            bash_script = f"cd {temp_dir_path} && git clone --depth 1 --branch {self.branch_or_tag_name} {self.github_repository_url}"
            result = subprocess.run(bash_script, shell=True,
                                    capture_output=True, text=True)
            log_technical_info(message=f"Downloaded stdout '{result.stdout}'")
            log_technical_info(message=f"Downloaded stderr '{result.stderr}'")
            git_last_commit_hash = get_git_head_hash(git_repository_path=temp_dir_path / self.repository_name)
            downloaded_tmp_project_path = temp_dir_path / self.repository_name
            shutil.copytree(downloaded_tmp_project_path, output_project_path, dirs_exist_ok=True)

        return git_last_commit_hash
