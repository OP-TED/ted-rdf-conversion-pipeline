from click.testing import CliRunner

from ted_sws.mapping_suite_processor.entrypoints.cmd_mapping_suite_processor import main as cli_main
from tests.unit.mapping_suite_processor.test_cmd_metadata_generator import __process_output_dir as \
    metadata__process_output_dir
from tests.unit.mapping_suite_processor.test_cmd_sparql_generator import __process_output_dir as \
    sparql__process_output_dir
from tests.unit.mapping_suite_processor.test_cmd_yarrrml2rml_converter import __process_output_dir as \
    rml__process_output_dir

cmdRunner = CliRunner()


def __process_output_dir(fake_repository_path, fake_mapping_suite_id):
    metadata__process_output_dir(fake_repository_path, fake_mapping_suite_id)
    sparql__process_output_dir(fake_repository_path, fake_mapping_suite_id)
    rml__process_output_dir(fake_repository_path, fake_mapping_suite_id)


def test_mapping_suite_processor(fake_mapping_suite_id, file_system_repository_path):
    response = cmdRunner.invoke(cli_main, [fake_mapping_suite_id, "--opt-mappings-folder", file_system_repository_path])
    assert response.exit_code == 0
    assert "SUCCESS" in response.output
    __process_output_dir(file_system_repository_path, fake_mapping_suite_id)


def test_mapping_suite_processor_with_invalid_id(invalid_mapping_suite_id, invalid_repository_path):
    response = cmdRunner.invoke(cli_main,
                                [invalid_mapping_suite_id, "--opt-mappings-folder", invalid_repository_path])
    assert response.exit_code == 1
    assert "FAILED" in response.output
