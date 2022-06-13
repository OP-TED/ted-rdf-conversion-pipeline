from ted_sws.notice_validator.entrypoints.cli.cmd_sparql_runner import main as cli_main
from tests.unit.notice_validator.cli import post_process


def test_cmd_sparql_runner(cli_runner, fake_mapping_suite_id, fake_repository_path, fake_rml_mapper):
    response = cli_runner.invoke(cli_main,
                                 [fake_mapping_suite_id, "--opt-mappings-folder", fake_repository_path])
    assert response.exit_code == 0
    print(response.output)
    assert "SUCCESS" in response.output

    post_process(fake_repository_path, fake_mapping_suite_id)


def test_cmd_sparql_runner_with_invalid_input(cli_runner, fake_repository_path, invalid_mapping_suite_id):
    response = cli_runner.invoke(cli_main,
                                 [invalid_mapping_suite_id, "--opt-mappings-folder", fake_repository_path])
    assert "FAILED" in response.output
