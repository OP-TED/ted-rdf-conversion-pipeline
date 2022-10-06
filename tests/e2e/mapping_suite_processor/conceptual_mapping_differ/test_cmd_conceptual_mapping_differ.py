import shutil
import tempfile
from pathlib import Path
from ted_sws.data_manager.adapters.mapping_suite_repository import MS_TRANSFORM_FOLDER_NAME, \
    MS_CONCEPTUAL_MAPPING_FILE_NAME
from ted_sws.mapping_suite_processor.entrypoints.cli.cmd_conceptual_mapping_differ import main as cli_main


def test_cmd_conceptual_mapping_differ(caplog, cli_runner, fake_test_mapping_suite_id, file_system_repository_path):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_mapping_suite_path = Path(temp_folder)
        shutil.copytree(file_system_repository_path, temp_mapping_suite_path, dirs_exist_ok=True)

        filepath = temp_mapping_suite_path / fake_test_mapping_suite_id / MS_TRANSFORM_FOLDER_NAME / MS_CONCEPTUAL_MAPPING_FILE_NAME

        response = cli_runner.invoke(cli_main,
                                     ["--mapping-suite-id", fake_test_mapping_suite_id, "--opt-mappings-folder",
                                      temp_mapping_suite_path, "--file", filepath, "--file", filepath,
                                      "--opt-output-folder", temp_folder])

        assert response.exit_code == 0
        assert "SUCCESS" in response.output

        response = cli_runner.invoke(cli_main,
                                     ["--mapping-suite-id", fake_test_mapping_suite_id, "--mapping-suite-id",
                                      fake_test_mapping_suite_id, "--opt-mappings-folder", temp_mapping_suite_path,
                                      "--opt-output-folder", temp_folder])

        assert response.exit_code == 0
        assert "SUCCESS" in response.output

        response = cli_runner.invoke(cli_main,
                                     ["--mapping-suite-id", fake_test_mapping_suite_id, "--opt-mappings-folder",
                                      temp_mapping_suite_path, "--file", filepath,
                                      "--opt-output-folder", temp_folder])

        assert response.exit_code == 0
        assert "SUCCESS" in response.output

        response = cli_runner.invoke(cli_main,
                                     ["--mapping-suite-id", "package_F03_test", "--opt-mappings-folder",
                                      temp_mapping_suite_path, "--branch", "main", "--branch", "main",
                                      "--opt-output-folder", temp_folder])

        assert response.exit_code == 0
        assert "SUCCESS" in response.output

        response = cli_runner.invoke(cli_main,
                                     ["--opt-mappings-folder", temp_mapping_suite_path,
                                      "--opt-output-folder", temp_folder])
        assert "FAILED" in response.output
        assert "Cannot do a diff" in response.output

        response = cli_runner.invoke(cli_main,
                                     ["--branch", "main", "--mapping-suite-id", "package_F03_test",
                                      "--opt-mappings-folder", temp_mapping_suite_path, "--opt-output-folder",
                                      temp_folder])

        assert response.exit_code == 0
        assert "SUCCESS" in response.output
