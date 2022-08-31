import os

import pytest

from ted_sws.notice_validator.entrypoints.cli.cmd_xpath_coverage_runner import run as cli_run, \
    DEFAULT_OUTPUT_PATH, DEFAULT_TEST_SUITE_REPORT_FOLDER


def post_process(fake_repository_path, fake_mapping_suite_id):
    base_path = fake_repository_path / fake_mapping_suite_id / DEFAULT_OUTPUT_PATH
    notice_report_path = base_path / "notice" / DEFAULT_TEST_SUITE_REPORT_FOLDER
    assert os.path.isdir(notice_report_path)
    report_files = []
    for filename in os.listdir(notice_report_path):
        if filename.startswith("xpath_cov"):
            report_files.append(filename)
            f = os.path.join(notice_report_path, filename)
            assert os.path.isfile(f)
            os.remove(f)
    assert len(report_files) == 2
    os.rmdir(notice_report_path)

    report_files = []
    for filename in os.listdir(base_path):
        if filename.startswith("xpath_cov"):
            report_files.append(filename)
            f = os.path.join(base_path, filename)
            assert os.path.isfile(f)
            os.remove(f)
    assert len(report_files) == 2


def test_cmd_xpath_coverage_runner(caplog, fake_mapping_suite_F03_id, fake_repository_path):
    cli_run(
        mapping_suite_id=fake_mapping_suite_F03_id,
        opt_mappings_folder=fake_repository_path
    )

    assert "SUCCESS" in caplog.text

    post_process(fake_repository_path, fake_mapping_suite_F03_id)


def test_cmd_xpath_coverage_runner_with_invalid_input(caplog, fake_repository_path, invalid_mapping_suite_id):
    with pytest.raises(FileNotFoundError):
        cli_run(
            mapping_suite_id=invalid_mapping_suite_id,
            opt_mappings_folder=fake_repository_path,
            opt_conceptual_mappings_file="invalid"
        )
        assert "FAILED" in caplog.text
