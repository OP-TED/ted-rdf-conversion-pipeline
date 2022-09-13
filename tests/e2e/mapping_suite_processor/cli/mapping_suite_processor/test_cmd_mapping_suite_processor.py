import shutil
import tempfile
from pathlib import Path

from ted_sws.mapping_suite_processor.entrypoints.cli.cmd_mapping_suite_processor import main as cli_main


def test_mapping_suite_processor(cli_runner, fake_mapping_suite_id, file_system_repository_path,
                                 ):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_mapping_suite_path = Path(temp_folder)
        shutil.copytree(file_system_repository_path, temp_mapping_suite_path, dirs_exist_ok=True)
        response = cli_runner.invoke(cli_main, [
            fake_mapping_suite_id,
            "--opt-mappings-folder", temp_mapping_suite_path
        ])
        assert response.exit_code == 0
        assert "SUCCESS" in response.output
        assert "FAILED" not in response.output


def test_mapping_suite_processor_with_invalid_id(cli_runner, invalid_mapping_suite_id, invalid_repository_path):
    response = cli_runner.invoke(cli_main, [invalid_mapping_suite_id, "--opt-mappings-folder", invalid_repository_path])
    assert response.exit_code == 1
    assert "FAILED" in response.output
