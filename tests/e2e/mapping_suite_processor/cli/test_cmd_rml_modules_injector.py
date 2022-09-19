import shutil
import tempfile
from pathlib import Path

from ted_sws.mapping_suite_processor.entrypoints.cli.cmd_rml_modules_injector import main as cli_main


def test_rml_modules_injector(cli_runner, fake_mapping_suite_id, file_system_repository_path, rml_modules_path):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_mapping_suite_path = Path(temp_folder)
        shutil.copytree(file_system_repository_path, temp_mapping_suite_path, dirs_exist_ok=True)

        response = cli_runner.invoke(cli_main, [fake_mapping_suite_id,
                                                "--opt-mappings-folder", temp_mapping_suite_path,
                                                "--opt-rml-modules-folder", rml_modules_path
                                                ])
        assert response.exit_code == 0
        assert "SUCCESS" in response.output


def test_rml_modules_injector_with_non_existing_input(cli_runner, file_system_repository_path, rml_modules_path):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_mapping_suite_path = Path(temp_folder)
        shutil.copytree(file_system_repository_path, temp_mapping_suite_path, dirs_exist_ok=True)

        response = cli_runner.invoke(cli_main, ["-i", "non_existing_dir/non_existing_file",
                                                "-o", "non_existing_dir",
                                                "--opt-rml-modules-folder", rml_modules_path,
                                                "--opt-mappings-folder", temp_mapping_suite_path])
        assert "No such file" in response.output


def test_rml_modules_injector_with_invalid_input(cli_runner, file_system_repository_path, fake_mapping_suite_id,
                                                 rml_modules_path):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_mapping_suite_path = Path(temp_folder)
        shutil.copytree(file_system_repository_path, temp_mapping_suite_path, dirs_exist_ok=True)

        response = cli_runner.invoke(cli_main, ["-i", str(temp_mapping_suite_path / fake_mapping_suite_id /
                                                          "transformation" / "invalid_conceptual_mappings.xlsx"),
                                                "--opt-rml-modules-folder", rml_modules_path,
                                                "--opt-mappings-folder", temp_mapping_suite_path])
        assert "FAILED" in response.output
