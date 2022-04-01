import os
import subprocess
from pathlib import Path

from click.testing import CliRunner

from ted_sws.notice_transformer.entrypoints.cmd_mapping_suite_transformer import transform_notice

cmdRunner = CliRunner()


def test_cmd_transformer(fake_mapping_suite_id, fake_repository_path):
    response = cmdRunner.invoke(transform_notice, [fake_mapping_suite_id, "--opt-mappings-path", fake_repository_path])
    assert response.exit_code == 0
    assert fake_mapping_suite_id in response.output
    assert "SUCCESS" in response.output


def test_cmd_transformer_with_not_package(fake_not_mapping_suite_id, fake_repository_path):
    response = cmdRunner.invoke(transform_notice,
                                [fake_not_mapping_suite_id, "--opt-mappings-path", fake_repository_path])
    assert "FAILED" in response.output
    assert "Not a MappingSuite" in response.output


def test_cmd_transformer_with_failed_package(fake_failed_mapping_suite_id, fake_repository_path):
    response = cmdRunner.invoke(transform_notice,
                                [fake_failed_mapping_suite_id, "--opt-mappings-path", fake_repository_path])
    assert "FAILED" in response.output


def test_cmd_transformer_with_no_suite_id(fake_repository_path, fake_mapping_suite_id):
    response = cmdRunner.invoke(transform_notice, ["--opt-mappings-path", fake_repository_path])
    assert response.exit_code == 0


def test_cmd_transformer_from_cli(fake_repository_path, cmd_transformer_path, fake_mapping_suite_id):
    cmd = f"cd {fake_repository_path} && pwd && ln -sf {cmd_transformer_path} transformer && ls -al && ./transformer --opt-mapping-suite-id={fake_mapping_suite_id} --opt-mappings-path=."
    response = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    print(response.stdout.decode('utf-8'))
    assert response.returncode == 0

    output_dir_path = fake_repository_path / fake_mapping_suite_id / "output"
    output_notice_path = output_dir_path / "notice.xml"
    assert os.path.isdir(output_dir_path)
    assert os.path.isfile(output_notice_path)
    os.remove(output_notice_path)
    os.rmdir(output_dir_path)

    os.remove(os.path.join(fake_repository_path, Path('transformer')))
