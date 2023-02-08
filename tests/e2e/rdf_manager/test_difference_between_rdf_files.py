import shutil
import tempfile
from pathlib import Path

from ted_sws.workbench_tools.rdf_differ.entrypoints.cli.cmd_rdf_differ import main as cli_main, DEFAULT_REPORT_FILE_NAME
from ted_sws.workbench_tools.rdf_differ.services.difference_between_rdf_files import generate_rdf_differ_html_report

CONTENT_FIRST_FILE = '<h2>Difference in the first file</h2>'
CONTENT_SECOND_FILE = '<h2>Difference in the second file</h2>'


def test_generate_rdf_differ_html_report(technical_mapping_f03_file_path, technical_mapping_f06_file_path):
    differences_between_files = generate_rdf_differ_html_report(technical_mapping_f03_file_path,
                                                                technical_mapping_f06_file_path)
    assert CONTENT_FIRST_FILE in differences_between_files
    assert CONTENT_SECOND_FILE in differences_between_files
    assert len(differences_between_files) > 10


def test_cmd_rdf_differ(cli_runner, technical_mapping_f03_file_path, technical_mapping_f06_file_path):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_folder_path = Path(temp_folder)
        shutil.copy(technical_mapping_f03_file_path, temp_folder_path)
        shutil.copy(technical_mapping_f06_file_path, temp_folder_path)

        response = cli_runner.invoke(cli_main, [str(temp_folder_path / technical_mapping_f03_file_path),
                                                str(temp_folder_path / technical_mapping_f06_file_path),
                                                "--output-folder", str(temp_folder_path)])
        assert response.exit_code == 0
        assert "SUCCESS" in response.output
        report_file_path = temp_folder_path / DEFAULT_REPORT_FILE_NAME.format(
            first_file=Path(technical_mapping_f03_file_path).stem,
            second_file=Path(technical_mapping_f06_file_path).stem
        )
        assert report_file_path.is_file()

        response = cli_runner.invoke(cli_main,
                                     ["invalid_file_1", "invalid_file_2", "--output-folder", str(temp_folder_path)])
        assert "FAILED" in response.output
