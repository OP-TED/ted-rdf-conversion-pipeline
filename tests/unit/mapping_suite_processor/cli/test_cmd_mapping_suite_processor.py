from ted_sws.mapping_suite_processor.entrypoints.cli.cmd_mapping_suite_processor import main as cli_main
from tests.unit.mapping_suite_processor.cli.test_cmd_metadata_generator import post_process as metadata_post_process
from tests.unit.mapping_suite_processor.cli.test_cmd_sparql_generator import post_process as sparql_post_process
from tests.unit.mapping_suite_processor.cli.test_cmd_yarrrml2rml_converter import post_process as rml_post_process


def post_process(fake_repository_path, fake_mapping_suite_id):
    metadata_post_process(fake_repository_path, fake_mapping_suite_id)
    sparql_post_process(fake_repository_path, fake_mapping_suite_id)
    rml_post_process(fake_repository_path, fake_mapping_suite_id)


def test_mapping_suite_processor(cli_runner, fake_mapping_suite_id, file_system_repository_path):
    response = cli_runner.invoke(cli_main, [
        fake_mapping_suite_id,
        "--opt-mappings-folder", file_system_repository_path
    ])
    print("K :: ", response.output)
    assert response.exit_code == 0
    assert "SUCCESS" in response.output
    assert "FAILED" not in response.output
    post_process(file_system_repository_path, fake_mapping_suite_id)


def test_mapping_suite_processor_with_invalid_id(cli_runner, invalid_mapping_suite_id, invalid_repository_path):
    response = cli_runner.invoke(cli_main, [invalid_mapping_suite_id, "--opt-mappings-folder", invalid_repository_path])
    assert response.exit_code == 1
    assert "FAILED" in response.output
