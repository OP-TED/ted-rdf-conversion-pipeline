import pytest

from ted_sws.data_manager.adapters.notice_repository import NoticeRepositoryInFileSystem
from tests import TEST_DATA_PATH

NOTICE_REPOSITORY_PATH = TEST_DATA_PATH / "notices"


@pytest.fixture
def transformed_complete_notice():
    test_notice_repository = NoticeRepositoryInFileSystem(repository_path=NOTICE_REPOSITORY_PATH)
    return test_notice_repository.get("396207_2018")
