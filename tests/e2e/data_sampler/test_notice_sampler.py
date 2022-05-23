import pathlib
import tempfile

from ted_sws.data_sampler.services.notice_sampler import store_notice_samples_in_file_system, \
    RESULT_NOTICE_SAMPLES_FOLDER_NAME


def test_notice_sampler(mongodb_client):
    with tempfile.TemporaryDirectory() as tmp_dirname:
        test_storage_path = pathlib.Path(tmp_dirname)
        store_notice_samples_in_file_system(mongodb_client=mongodb_client,
                                            storage_path=test_storage_path,
                                            top_k=10)
        result_path = test_storage_path / RESULT_NOTICE_SAMPLES_FOLDER_NAME
        assert result_path.exists()
