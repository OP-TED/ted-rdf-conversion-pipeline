import os

from ted_sws.workbench_tools.rml_to_html.cli import main as cli_main, \
    DEFAULT_OUTPUT_PATH, HTML_REPORT


def post_process(file_system_repository_path, fake_mapping_suite_id):
    base_path = file_system_repository_path / fake_mapping_suite_id / DEFAULT_OUTPUT_PATH
    report_path = base_path / HTML_REPORT
    assert os.path.isfile(report_path)
    os.remove(report_path)


def test_cmd_rml_report_generator(cli_runner, fake_mapping_suite_id, file_system_repository_path):
    response = cli_runner.invoke(cli_main,
                                 [fake_mapping_suite_id, "--opt-mappings-folder", file_system_repository_path])
    assert response.exit_code == 0
    assert "SUCCESS" in response.output

    post_process(file_system_repository_path, fake_mapping_suite_id)


def test_cmd_rml_report_generator_with_invalid_input(cli_runner, file_system_repository_path, invalid_mapping_suite_id):
    response = cli_runner.invoke(cli_main,
                                 [invalid_mapping_suite_id, "--opt-mappings-folder", file_system_repository_path])
    assert "FAILED" in response.output
