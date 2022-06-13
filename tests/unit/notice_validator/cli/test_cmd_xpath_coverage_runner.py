import os
import pytest

from ted_sws.notice_validator.entrypoints.cli.cmd_xpath_coverage_runner import run as cli_run, \
    DEFAULT_OUTPUT_PATH, DEFAULT_TEST_SUITE_REPORT_FOLDER
from ted_sws.event_manager.adapters.logger import Logger
import logging

TEST_LOGGER = Logger(name="TEST_MAPPING_RUNNER", level=logging.INFO)
TEST_LOGGER.get_logger().propagate = True


def post_process(fake_repository_path, fake_mapping_suite_id):
    base_path = fake_repository_path / fake_mapping_suite_id / DEFAULT_OUTPUT_PATH / "notice"
    report_path = base_path / DEFAULT_TEST_SUITE_REPORT_FOLDER
    assert os.path.isdir(report_path)
    report_files = []
    for filename in os.listdir(report_path):
        if filename.startswith("xpath_cov"):
            report_files.append(filename)
            f = os.path.join(report_path, filename)
            assert os.path.isfile(f)
            os.remove(f)
    assert len(report_files) == 1
    os.rmdir(report_path)


def test_cmd_xpath_coverage_runner(caplog, fake_mapping_suite_F03_id, fake_repository_path, fake_xslt_transformer):
    cli_run(
        mapping_suite_id=fake_mapping_suite_F03_id,
        opt_mappings_folder=fake_repository_path,
        xslt_transformer=fake_xslt_transformer,
        logger=TEST_LOGGER
    )

    assert "SUCCESS" in caplog.text

    post_process(fake_repository_path, fake_mapping_suite_F03_id)


def test_cmd_xpath_coverage_runner_with_invalid_input(caplog, fake_repository_path, invalid_mapping_suite_id,
                                                      fake_xslt_transformer):
    with pytest.raises(FileNotFoundError):
        cli_run(
            mapping_suite_id=invalid_mapping_suite_id,
            opt_mappings_folder=fake_repository_path,
            opt_conceptual_mappings_file="invalid",
            xslt_transformer=fake_xslt_transformer,
            logger=TEST_LOGGER
        )
        assert "FAILED" in caplog.text

