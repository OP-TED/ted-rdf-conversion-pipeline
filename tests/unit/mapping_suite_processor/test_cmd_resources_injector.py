import os

from click.testing import CliRunner

from ted_sws.mapping_suite_processor.entrypoints.cli.cmd_resources_injector import main as inject_resources

cmdRunner = CliRunner()


def __process_output_dir(fake_repository_path, fake_mapping_suite_id):
    output_dir_path = fake_repository_path / fake_mapping_suite_id / "transformation" / "resources"
    assert os.path.isdir(output_dir_path)
    for filename in os.listdir(output_dir_path):
        f = os.path.join(output_dir_path, filename)
        if os.path.isfile(f):
            os.remove(f)


def test_resources_injector(fake_mapping_suite_id, file_system_repository_path):
    response = cmdRunner.invoke(inject_resources, [fake_mapping_suite_id, "--opt-mappings-folder",
                                                   file_system_repository_path])
    assert response.exit_code == 0
    assert "SUCCESS" in response.output
    __process_output_dir(file_system_repository_path, fake_mapping_suite_id)


def test_sparql_generator_with_non_existing_input(file_system_repository_path):
    response = cmdRunner.invoke(inject_resources, ["-i", "non_existing_dir/non_existing_file",
                                                   "-o", "non_existing_dir",
                                                   "--opt-mappings-folder", file_system_repository_path])
    assert "No such file" in response.output


def test_sparql_generator_with_invalid_input(file_system_repository_path, fake_mapping_suite_id):
    response = cmdRunner.invoke(inject_resources, ["-i", str(file_system_repository_path / fake_mapping_suite_id /
                                                             "transformation" / "invalid_conceptual_mappings.xlsx"),
                                                   "--opt-mappings-folder", file_system_repository_path])
    assert "FAILED" in response.output
