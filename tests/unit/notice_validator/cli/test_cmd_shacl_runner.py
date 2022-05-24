import os

from ted_sws.notice_validator.entrypoints.cli.cmd_shacl_runner import main as cli_main, \
    DEFAULT_TEST_SUITE_REPORT_FOLDER, DEFAULT_OUTPUT_PATH


def post_process(fake_repository_path, fake_mapping_suite_id):
    base_path = fake_repository_path / fake_mapping_suite_id / DEFAULT_OUTPUT_PATH / "example"
    report_path = base_path / DEFAULT_TEST_SUITE_REPORT_FOLDER
    assert os.path.isdir(report_path)
    for filename in os.listdir(report_path):
        f = os.path.join(report_path, filename)
        assert os.path.isfile(f)
        os.remove(f)
    os.rmdir(report_path)


def test_cmd_shacl_runner(cli_runner, fake_mapping_suite_id, fake_repository_path):
    response = cli_runner.invoke(cli_main,
                                 [fake_mapping_suite_id, "--opt-mappings-folder", fake_repository_path])
    assert response.exit_code == 0
    assert "SUCCESS" in response.output

    post_process(fake_repository_path, fake_mapping_suite_id)


def test_cmd_shacl_runner_with_invalid_input(cli_runner, fake_repository_path, invalid_mapping_suite_id):
    response = cli_runner.invoke(cli_main,
                                 [invalid_mapping_suite_id, "--opt-mappings-folder", fake_repository_path])
    assert "FAILED" in response.output
