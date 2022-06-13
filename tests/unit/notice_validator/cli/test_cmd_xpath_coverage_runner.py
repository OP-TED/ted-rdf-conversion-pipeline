import os

from ted_sws.notice_validator.entrypoints.cli.cmd_xpath_coverage_runner import main as cli_main, \
    DEFAULT_OUTPUT_PATH, DEFAULT_TEST_SUITE_REPORT_FOLDER


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


def test_cmd_xpath_coverage_runner(cli_runner, fake_mapping_suite_F03_id, fake_repository_path):
    response = cli_runner.invoke(cli_main,
                                 [fake_mapping_suite_F03_id, "--opt-mappings-folder", fake_repository_path])
    assert response.exit_code == 0
    assert "SUCCESS" in response.output

    post_process(fake_repository_path, fake_mapping_suite_F03_id)


def test_cmd_xpath_coverage_runner_with_invalid_input(cli_runner, fake_repository_path, invalid_mapping_suite_id):
    response = cli_runner.invoke(cli_main,
                                 [invalid_mapping_suite_id, "--opt-mappings-folder", fake_repository_path,
                                  "--opt-conceptual-mappings-file", "invalid"])
    assert "FAILED" in response.output
