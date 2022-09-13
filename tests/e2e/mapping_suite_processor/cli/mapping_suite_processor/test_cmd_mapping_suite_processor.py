import shutil
import tempfile
from pathlib import Path

from ted_sws.mapping_suite_processor.entrypoints.cli.cmd_mapping_suite_processor import main as cli_main


def test_mapping_suite_processor(cli_runner, fake_mapping_suite_id, file_system_repository_path, fake_notice_id,
                                 rml_modules_path):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_mapping_suite_path = Path(temp_folder)
        shutil.copytree(file_system_repository_path, temp_mapping_suite_path, dirs_exist_ok=True)

        response = cli_runner.invoke(cli_main, [
            fake_mapping_suite_id,
            "--opt-mappings-folder", temp_mapping_suite_path,
            "--opt-rml-modules-folder", rml_modules_path
        ])
        assert response.exit_code == 0
        assert "SUCCESS" in response.output
        assert "FAILED" not in response.output

        response = cli_runner.invoke(cli_main, [
            fake_mapping_suite_id,
            "--notice-id", fake_notice_id,
            "--opt-mappings-folder", temp_mapping_suite_path,
            "--opt-rml-modules-folder", rml_modules_path
        ])
        assert response.exit_code == 0
        assert "SUCCESS" in response.output
        assert "FAILED" not in response.output

        response = cli_runner.invoke(cli_main, [
            fake_mapping_suite_id,
            "--notice-id", fake_notice_id,
            "--group", "inject_resources,invalid_group",
            "--opt-mappings-folder", temp_mapping_suite_path,
            "--opt-rml-modules-folder", rml_modules_path
        ])
        assert response.exit_code == 0
        assert "SUCCESS" in response.output
        assert "FAILED" not in response.output
        assert "groups will be skipped (invalid): invalid_group" in response.output

        response = cli_runner.invoke(cli_main, [
            fake_mapping_suite_id,
            "--notice-id", fake_notice_id,
            "--command", "invalid_command,resources_injector",
            "--opt-mappings-folder", temp_mapping_suite_path,
            "--opt-rml-modules-folder", rml_modules_path
        ])
        assert response.exit_code == 0
        assert "SUCCESS" in response.output
        assert "FAILED" not in response.output
        assert "commands will be skipped (invalid): invalid_command" in response.output


def test_mapping_suite_processor_with_invalid_id(cli_runner, invalid_mapping_suite_id, invalid_repository_path):
    response = cli_runner.invoke(cli_main, [invalid_mapping_suite_id, "--opt-mappings-folder", invalid_repository_path])
    assert response.exit_code == 1
    assert "FAILED" in response.output
