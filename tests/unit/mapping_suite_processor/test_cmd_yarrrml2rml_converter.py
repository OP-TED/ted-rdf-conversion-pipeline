import os

from click.testing import CliRunner

from ted_sws.mapping_suite_processor.entrypoints.cmd_yarrrml2rml_converter import main as convert

cmdRunner = CliRunner()


def __process_output_dir(fake_repository_path, fake_mapping_suite_id):
    output_dir_path = fake_repository_path / fake_mapping_suite_id / "transformation" / "mappings"
    output_notice_path = output_dir_path / "mappings.rml.ttl"
    assert os.path.isdir(output_dir_path)
    assert os.path.isfile(output_notice_path)
    os.remove(output_notice_path)


def test_cmd_converter(fake_mapping_suite_id, file_system_repository_path):
    response = cmdRunner.invoke(convert, [fake_mapping_suite_id, "--opt-mappings-path", file_system_repository_path])
    assert response.exit_code == 0
    assert "SUCCESS" in response.output
    __process_output_dir(file_system_repository_path, fake_mapping_suite_id)


def test_cmd_converter_with_invalid_output(fake_mapping_suite_id, file_system_repository_path):
    response = cmdRunner.invoke(convert, [fake_mapping_suite_id, "-o", "non_existing_dir/non_existing_file",
                                          "--opt-mappings-path", file_system_repository_path])
    assert "FAILED" in response.output


def test_cmd_converter_with_invalid_input(file_system_repository_path):
    response = cmdRunner.invoke(convert, ["-i", "non_existing_dir/non_existing_file",
                                          "-o", "non_existing_dir/non_existing_file",
                                          "--opt-mappings-path", file_system_repository_path])
    assert "No such YARRRML file" in response.output
