import os
from pathlib import Path

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


def test_cmd_transformer_with_invalid_serialization(fake_mapping_suite_id, fake_repository_path):
    response = cmdRunner.invoke(
        transform, [
            fake_mapping_suite_id, "invalid-turtle",
            "--opt-mappings-path", fake_repository_path
        ]
    )
    assert "No such serialization format" in response.output

    response = cmdRunner.invoke(
        transform, [
            "--opt-mapping-suite-id", fake_mapping_suite_id,
            "--opt-mappings-path", fake_repository_path,
            "--opt-serialization-format", "invalid-turtle"
        ]
    )
    assert "No such serialization format" in response.output


def test_cmd_transformer_with_not_package(fake_not_mapping_suite_id, fake_fail_repository_path):
    response = cmdRunner.invoke(transform,
                                [fake_not_mapping_suite_id, "--opt-mappings-path", fake_fail_repository_path])
    assert "FAILED" in response.output
    assert "Not a MappingSuite" in response.output


def test_cmd_transformer_with_failed_package(fake_failed_mapping_suite_id, fake_fail_repository_path):
    response = cmdRunner.invoke(transform,
                                [fake_failed_mapping_suite_id, "--opt-mappings-path", fake_fail_repository_path])
    assert "FAILED" in response.output


def test_cmd_transformer_with_no_suite_id(fake_repository_path):
    response = cmdRunner.invoke(transform, ["--opt-mappings-path", fake_repository_path])
    assert response.exit_code == 0
    fs_repository_path = Path(os.path.realpath(fake_repository_path))
    for suite_id in os.listdir(fs_repository_path):
        __process_output_dir(fake_repository_path, suite_id)
