import os

from click.testing import CliRunner

from ted_sws.notice_transformer.entrypoints.cmd_mapping_runner import main as transform
from tests.unit.notice_transformer.test_cmd_mapping_runner import __process_output_dir

cmdRunner = CliRunner()


def test_cmd_transformer(fake_mapping_suite_id, fake_repository_path):
    response = cmdRunner.invoke(transform, [fake_mapping_suite_id, "--opt-mappings-folder", fake_repository_path])
    assert response.exit_code == 0
    assert fake_mapping_suite_id in response.output
    assert "SUCCESS" in response.output
    __process_output_dir(fake_repository_path, fake_mapping_suite_id)
