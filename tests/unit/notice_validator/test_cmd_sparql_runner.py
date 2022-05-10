import os

from click.testing import CliRunner

from ted_sws.notice_validator.entrypoints.cli.cmd_sparql_runner import main as cli_main, \
    DEFAULT_TEST_SUITE_REPORT_FOLDER, DEFAULT_SPARQL_REPORTS_FOLDER, DEFAULT_OUTPUT_PATH

cmdRunner = CliRunner()


def __process_output_dir(fake_repository_path, fake_mapping_suite_id):
    base_path = fake_repository_path / fake_mapping_suite_id / DEFAULT_OUTPUT_PATH / "example"
    report_path = base_path / DEFAULT_SPARQL_REPORTS_FOLDER
    assert os.path.isdir(report_path)
    for r in os.listdir(report_path):
        d = os.path.join(report_path, r)
        assert os.path.isdir(d)
        for filename in os.listdir(d):
            f = os.path.join(d, filename)
            if os.path.isfile(f):
                os.remove(f)
        os.rmdir(d)
    os.rmdir(report_path)

    report_path = base_path / DEFAULT_TEST_SUITE_REPORT_FOLDER
    assert os.path.isdir(report_path)
    for filename in os.listdir(report_path):
        f = os.path.join(report_path, filename)
        assert os.path.isfile(f)
        os.remove(f)
    os.rmdir(report_path)


def test_cmd_sparql_runner(fake_mapping_suite_id, fake_repository_path):
    response = cmdRunner.invoke(cli_main,
                                [fake_mapping_suite_id, "--opt-mappings-folder", fake_repository_path])
    assert response.exit_code == 0
    assert "SUCCESS" in response.output

    __process_output_dir(fake_repository_path, fake_mapping_suite_id)


def test_cmd_sparql_runner_with_invalid_input(fake_repository_path, invalid_mapping_suite_id):
    response = cmdRunner.invoke(cli_main,
                                [invalid_mapping_suite_id, "--opt-mappings-folder", fake_repository_path])
    assert "FAILED" in response.output
