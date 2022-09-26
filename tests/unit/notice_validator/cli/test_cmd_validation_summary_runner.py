import os
import shutil
import tempfile
from pathlib import Path
from ted_sws.notice_validator.entrypoints.cli.cmd_validation_summary_runner import main as cli_main, \
    DEFAULT_OUTPUT_PATH, DEFAULT_TEST_SUITE_REPORT_FOLDER


def post_process_for_notice(fake_repository_path, fake_mapping_suite_id, fake_validation_notice_id):
    base_path = fake_repository_path / fake_mapping_suite_id / DEFAULT_OUTPUT_PATH
    notice_report_path = base_path / fake_validation_notice_id / DEFAULT_TEST_SUITE_REPORT_FOLDER
    assert os.path.isdir(notice_report_path)
    report_files = []
    for filename in os.listdir(notice_report_path):
        if filename.startswith("validation_summary_report"):
            report_files.append(filename)
            f = os.path.join(notice_report_path, filename)
            assert os.path.isfile(f)
            os.remove(f)
    assert len(report_files) == 2


def test_cmd_validation_summary_runner_for_notice(cli_runner, fake_validation_mapping_suite_id,
                                                  fake_validation_repository_path, fake_validation_notice_id):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_mapping_suite_path = Path(temp_folder)
        shutil.copytree(fake_validation_repository_path, temp_mapping_suite_path, dirs_exist_ok=True)
        response = cli_runner.invoke(cli_main,
                                     [fake_validation_mapping_suite_id, "--notice-id", fake_validation_notice_id,
                                      "--opt-mappings-folder", temp_mapping_suite_path])

        assert response.exit_code == 0
        assert "SUCCESS" in response.output

        post_process_for_notice(temp_mapping_suite_path, fake_validation_mapping_suite_id,
                                fake_validation_notice_id)


def test_cmd_validation_summary_runner_for_mapping_suite(cli_runner, fake_validation_mapping_suite_id,
                                                         fake_validation_repository_path, fake_validation_notice_id):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_mapping_suite_path = Path(temp_folder)
        shutil.copytree(fake_validation_repository_path, temp_mapping_suite_path, dirs_exist_ok=True)

        response = cli_runner.invoke(cli_main, [fake_validation_mapping_suite_id, "--notice-aggregate", True,
                                                "--opt-mappings-folder", temp_mapping_suite_path])
        assert response.exit_code == 0
        assert "SUCCESS" in response.output

        output_path = temp_mapping_suite_path / fake_validation_mapping_suite_id / DEFAULT_OUTPUT_PATH

        html_mapping_suite_report = output_path / "validation_summary_report.html"
        assert os.path.isfile(html_mapping_suite_report)
        os.remove(html_mapping_suite_report)

        json_mapping_suite_report = output_path / "validation_summary_report.json"
        assert os.path.isfile(json_mapping_suite_report)
        os.remove(json_mapping_suite_report)

        for resource in output_path.iterdir():
            if resource.is_dir():
                notice_id = resource.stem
                post_process_for_notice(temp_mapping_suite_path, fake_validation_mapping_suite_id, notice_id)
