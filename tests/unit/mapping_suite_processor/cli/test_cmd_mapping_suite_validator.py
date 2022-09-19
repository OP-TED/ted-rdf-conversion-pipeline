import shutil
import tempfile
from pathlib import Path

from ted_sws.data_manager.adapters.mapping_suite_repository import MS_TRANSFORM_FOLDER_NAME, MS_MAPPINGS_FOLDER_NAME
from ted_sws.mapping_suite_processor.entrypoints.cli.cmd_mapping_suite_validator import main as cli_main, \
    MS_VALIDATOR_ERROR_EXIT_CODE
from tests import TEST_DATA_PATH


def test_mapping_suite_validator(cli_runner, mapping_suite_id):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_mapping_suite_path = Path(temp_folder) / mapping_suite_id
        shutil.copytree(Path(TEST_DATA_PATH) / mapping_suite_id, temp_mapping_suite_path, dirs_exist_ok=True)
        response = cli_runner.invoke(cli_main, [mapping_suite_id, "--opt-mappings-folder",
                                                temp_folder])
        assert response.exit_code == 0
        assert "SUCCESS" in response.output

        with open(temp_mapping_suite_path / MS_TRANSFORM_FOLDER_NAME / MS_MAPPINGS_FOLDER_NAME / "new_file.txt",
                  "w+") as new_file:
            new_file.write("TEXT")

        response = cli_runner.invoke(cli_main, [mapping_suite_id, "--opt-mappings-folder",
                                                temp_folder])
        assert response.exit_code == MS_VALIDATOR_ERROR_EXIT_CODE
        assert "FAILED" in response.output
