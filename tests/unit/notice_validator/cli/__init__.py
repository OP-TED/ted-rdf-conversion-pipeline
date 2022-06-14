import os

from ted_sws.notice_validator.entrypoints.cli import DEFAULT_TEST_SUITE_REPORT_FOLDER, DEFAULT_OUTPUT_PATH


def post_process(fake_repository_path, fake_mapping_suite_id):
    base_path = fake_repository_path / fake_mapping_suite_id / DEFAULT_OUTPUT_PATH / "notice"
    report_path = base_path / DEFAULT_TEST_SUITE_REPORT_FOLDER
    assert os.path.isdir(report_path)
    for filename in os.listdir(report_path):
        f = os.path.join(report_path, filename)
        assert os.path.isfile(f)
        os.remove(f)
    os.rmdir(report_path)
