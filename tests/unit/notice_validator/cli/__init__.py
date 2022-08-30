import os

from ted_sws.notice_validator.entrypoints.cli import DEFAULT_TEST_SUITE_REPORT_FOLDER, DEFAULT_OUTPUT_PATH


def post_process(fake_repository_path, fake_mapping_suite_id, file_mask=None, remove_dir=True):
    base_path = fake_repository_path / fake_mapping_suite_id / DEFAULT_OUTPUT_PATH / "notice"
    report_path = base_path / DEFAULT_TEST_SUITE_REPORT_FOLDER
    assert os.path.isdir(report_path)
    for filename in os.listdir(report_path):
        if not file_mask or filename.startswith(file_mask):
            f = os.path.join(report_path, filename)
            assert os.path.isfile(f)
            os.remove(f)
    if remove_dir:
        os.rmdir(report_path)
