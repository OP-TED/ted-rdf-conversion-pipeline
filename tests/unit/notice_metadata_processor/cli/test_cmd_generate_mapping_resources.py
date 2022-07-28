import json
import os
import pathlib

from ted_sws.data_manager.entrypoints.cli.cmd_generate_mapping_resources import run as cli_run, main as cli_main
from tests.fakes.fake_triple_store import FakeTripleStoreEndpoint


def post_process(fake_repository_path, fake_mapping_suite_id):
    output_dir_path = fake_repository_path / fake_mapping_suite_id / "transformation" / "resources"
    assert os.path.isdir(output_dir_path)
    for filename in os.listdir(output_dir_path):
        f = os.path.join(output_dir_path, filename)
        if os.path.isfile(f) and filename != "data.json":
            os.remove(f)


def test_generate_mapping_resources(tmp_path, queries_folder_path):
    output_folder_path = tmp_path
    cli_run(triple_store=FakeTripleStoreEndpoint(), opt_queries_folder=str(queries_folder_path),
            opt_output_folder=str(output_folder_path))
    generated_file_paths = list(pathlib.Path(output_folder_path).rglob("*.json"))

    assert len(generated_file_paths) == 1
    assert "buyer_legal_type" == generated_file_paths[0].stem
    assert ".json" in str(generated_file_paths[0])

    generated_file_content = json.loads(pathlib.Path(output_folder_path / "buyer_legal_type.json").read_bytes())

    assert isinstance(generated_file_content, dict)
    assert "results" in generated_file_content.keys()
    assert generated_file_content["results"] == "awesome results"


def test_generate_mapping_resources_cli(cli_runner, fake_mapping_suite_id, file_system_repository_path):
    response = cli_runner.invoke(cli_main,
                                 [fake_mapping_suite_id, "--opt-mappings-folder", file_system_repository_path])
    assert response.exit_code == 0

    #post_process(file_system_repository_path, fake_mapping_suite_id)


def test_generate_mapping_resources_with_invalid_mapping(cli_runner, invalid_mapping_suite_id,
                                                         file_system_repository_path):
    response = cli_runner.invoke(cli_main,
                                 [invalid_mapping_suite_id, "--opt-mappings-folder", file_system_repository_path])
    assert "FAILED" in response.output
