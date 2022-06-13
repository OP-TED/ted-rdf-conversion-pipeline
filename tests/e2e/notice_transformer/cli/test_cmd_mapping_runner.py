from ted_sws.notice_transformer.entrypoints.cli.cmd_mapping_runner import main as cli_main
from tests.unit.notice_transformer.cli.test_cmd_mapping_runner import post_process


def test_cmd_transformer(cli_runner, fake_mapping_suite_id, fake_repository_path):
    response = cli_runner.invoke(cli_main, [fake_mapping_suite_id, "--opt-mappings-folder", fake_repository_path])
    assert response.exit_code == 0
    assert fake_mapping_suite_id in response.output
    assert "SUCCESS" in response.output
    post_process(fake_repository_path, fake_mapping_suite_id)
