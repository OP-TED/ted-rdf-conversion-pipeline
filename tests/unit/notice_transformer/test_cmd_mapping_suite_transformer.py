from ted_sws.notice_transformer.entrypoints.cmd_mapping_suite_transformer import transform_notice
from click.testing import CliRunner

cmdRunner = CliRunner()


def test_cmd_transformer(fake_mapping_suite_id, fake_repository_path):
    response = cmdRunner.invoke(transform_notice, [fake_mapping_suite_id, "--opt-mappings-path", fake_repository_path])
    print(response.output)
    assert response.exit_code == 0
    assert fake_mapping_suite_id in response.output
    assert "SUCCESS" in response.output
