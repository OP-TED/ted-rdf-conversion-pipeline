import os

from click.testing import CliRunner

from ted_sws.notice_transformer.entrypoints.cmd_mapping_suite_transformer import main as transform

cmdRunner = CliRunner()


def __process_output_dir(fake_repository_path, fake_mapping_suite_id):
    output_dir_path = fake_repository_path / fake_mapping_suite_id / "output" / "notice"
    output_notice_path = output_dir_path / "notice.ttl"
    assert os.path.isdir(output_dir_path)
    assert os.path.isfile(output_notice_path)
    os.remove(output_notice_path)
    os.rmdir(output_dir_path)


def test_cmd_transformer(fake_mapping_suite_id, fake_repository_path):
    response = cmdRunner.invoke(transform, [fake_mapping_suite_id, "--opt-mappings-path", fake_repository_path])
    assert response.exit_code == 0
    assert fake_mapping_suite_id in response.output
    assert "SUCCESS" in response.output
    __process_output_dir(fake_repository_path, fake_mapping_suite_id)
