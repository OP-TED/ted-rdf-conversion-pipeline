from ted_sws.notice_validator.entrypoints.cli.cmd_xpath_coverage_runner import main as cli_main
from tests.unit.notice_validator.cli.test_cmd_xpath_coverage_runner import post_process


def test_cmd_xpath_coverage_runner(cli_runner, fake_mapping_suite_F03_id, fake_repository_path):
    response = cli_runner.invoke(cli_main,
                                 [fake_mapping_suite_F03_id, "--opt-mappings-folder", fake_repository_path])
    assert response.exit_code == 0
    assert "SUCCESS" in response.output

    post_process(fake_repository_path, fake_mapping_suite_F03_id)
