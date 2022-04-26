import json
import os
import pathlib

from click.testing import CliRunner

from ted_sws.data_manager.entrypoints.cmd_generate_mapping_resources import run as cli_run, main as cli_main
from tests import TEST_DATA_PATH
from tests.fakes.fake_triple_store import FakeTripleStore


def __process_output_dir(fake_repository_path, fake_mapping_suite_id):
    output_dir_path = fake_repository_path / fake_mapping_suite_id / "transformation" / "resources"
    assert os.path.isdir(output_dir_path)
    for filename in os.listdir(output_dir_path):
        f = os.path.join(output_dir_path, filename)
        if os.path.isfile(f):
            os.remove(f)


def test_generate_mapping_resources(tmp_path):
    queries_folder_path = TEST_DATA_PATH / "sparql_queries"
    output_folder_path = tmp_path
    cli_run(triple_store=FakeTripleStore(), opt_queries_folder=str(queries_folder_path),
            opt_output_folder=str(output_folder_path))
    generated_file_paths = list(pathlib.Path(output_folder_path).rglob("*.json"))

    assert len(generated_file_paths) == 1
    assert "buyer_legal_type" == generated_file_paths[0].stem
    assert ".json" in str(generated_file_paths[0])

    generated_file_content = json.loads(pathlib.Path(output_folder_path / "buyer_legal_type.json").read_bytes())

    assert isinstance(generated_file_content, dict)
    assert "results" in generated_file_content.keys()
    assert generated_file_content["results"] == "awesome results"


def test_generate_mapping_resources_cli(fake_mapping_suite_id, file_system_repository_path):
    cli = CliRunner()
    response = cli.invoke(cli_main, [fake_mapping_suite_id, "--opt-mappings-path", file_system_repository_path])
    assert response.exit_code == 0

    __process_output_dir(file_system_repository_path, fake_mapping_suite_id)


def test_generate_mapping_resources_with_invalid_mapping(invalid_mapping_suite_id, file_system_repository_path):
    cli = CliRunner()
    response = cli.invoke(cli_main, [invalid_mapping_suite_id, "--opt-mappings-path", file_system_repository_path])
    assert "FAILED" in response.output
