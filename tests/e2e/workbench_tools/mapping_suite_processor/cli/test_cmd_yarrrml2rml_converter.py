import shutil
import tempfile
from pathlib import Path

from ted_sws.workbench_tools.mapping_suite_processor.entrypoints.cli.cmd_yarrrml2rml_converter import main as cli_main


def test_cmd_converter(cli_runner, fake_test_mapping_suite_id, file_system_repository_path):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_mapping_suite_path = Path(temp_folder)
        shutil.copytree(file_system_repository_path, temp_mapping_suite_path, dirs_exist_ok=True)

        response = cli_runner.invoke(cli_main,
                                     [fake_test_mapping_suite_id, "--opt-mappings-folder", temp_mapping_suite_path])
        assert response.exit_code == 0
        assert "SUCCESS" in response.output

        output_dir_path = temp_mapping_suite_path / fake_test_mapping_suite_id / "transformation" / "mappings"
        output_file_path = output_dir_path / "mappings.rml.ttl"
        assert output_dir_path.is_dir()
        assert output_file_path.is_file()


def test_cmd_converter_with_non_existing_output(cli_runner, fake_test_mapping_suite_id, file_system_repository_path):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_mapping_suite_path = Path(temp_folder)
        shutil.copytree(file_system_repository_path, temp_mapping_suite_path, dirs_exist_ok=True)

        response = cli_runner.invoke(cli_main, [fake_test_mapping_suite_id, "-o", "non_existing_dir/non_existing_file",
                                                "--opt-mappings-folder", temp_mapping_suite_path])
        assert "FAILED" in response.output


def test_cmd_converter_with_non_existing_input(cli_runner, file_system_repository_path):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_mapping_suite_path = Path(temp_folder)
        shutil.copytree(file_system_repository_path, temp_mapping_suite_path, dirs_exist_ok=True)

        response = cli_runner.invoke(cli_main, ["-i", "non_existing_dir/non_existing_file1",
                                                "-o", "non_existing_dir/non_existing_file2",
                                                "--opt-mappings-folder", temp_mapping_suite_path])
        assert "No such YARRRML file" in response.output
