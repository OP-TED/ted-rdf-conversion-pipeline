import os

from click.testing import CliRunner

from ted_sws.mapping_suite_processor.entrypoints.cmd_metadata_generator import main as generate

cmdRunner = CliRunner()


def __process_output_dir(fake_repository_path, fake_mapping_suite_id):
    output_dir_path = fake_repository_path / fake_mapping_suite_id
    output_file_path = output_dir_path / "metadata.json"
    assert os.path.isdir(output_dir_path)
    assert os.path.isfile(output_file_path)
    os.remove(output_file_path)


def test_metadata_generator(fake_mapping_suite_id, file_system_repository_path):
    response = cmdRunner.invoke(generate, [fake_mapping_suite_id, "--opt-mappings-path", file_system_repository_path])
    assert response.exit_code == 0
    assert "SUCCESS" in response.output
    __process_output_dir(file_system_repository_path, fake_mapping_suite_id)


def test_metadata_generator_with_non_existing_input(file_system_repository_path):
    response = cmdRunner.invoke(generate, ["-i", "non_existing_dir/non_existing_file",
                                           "-o", "non_existing_dir/non_existing_file",
                                           "--opt-mappings-path", file_system_repository_path])
    assert "No such file" in response.output


def test_sparql_generator_with_invalid_input(file_system_repository_path, fake_mapping_suite_id):
    response = cmdRunner.invoke(generate, ["-i", str(file_system_repository_path / fake_mapping_suite_id /
                                                     "transformation" / "invalid_conceptual_mappings.xlsx"),
                                           "--opt-mappings-path", file_system_repository_path])
    assert "FAILED" in response.output
