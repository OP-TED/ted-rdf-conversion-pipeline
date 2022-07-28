import os

from ted_sws.mapping_suite_processor.entrypoints.cli.cmd_yarrrml2rml_converter import main as cli_main


def post_process(fake_repository_path, fake_mapping_suite_id):
    output_dir_path = fake_repository_path / fake_mapping_suite_id / "transformation" / "mappings"
    output_file_path = output_dir_path / "mappings.rml.ttl"
    assert os.path.isdir(output_dir_path)
    assert os.path.isfile(output_file_path)
    os.remove(output_file_path)


def test_cmd_converter(cli_runner, fake_mapping_suite_id, file_system_repository_path):
    response = cli_runner.invoke(cli_main,
                                 [fake_mapping_suite_id, "--opt-mappings-folder", file_system_repository_path])
    assert response.exit_code == 0
    assert "SUCCESS" in response.output
    post_process(file_system_repository_path, fake_mapping_suite_id)


def test_cmd_converter_with_non_existing_output(cli_runner, fake_mapping_suite_id, file_system_repository_path):
    response = cli_runner.invoke(cli_main, [fake_mapping_suite_id, "-o", "non_existing_dir/non_existing_file",
                                            "--opt-mappings-folder", file_system_repository_path])
    assert "FAILED" in response.output


def test_cmd_converter_with_non_existing_input(cli_runner, file_system_repository_path):
    response = cli_runner.invoke(cli_main, ["-i", "non_existing_dir/non_existing_file",
                                            "-o", "non_existing_dir/non_existing_file",
                                            "--opt-mappings-folder", file_system_repository_path])
    assert "No such YARRRML file" in response.output
