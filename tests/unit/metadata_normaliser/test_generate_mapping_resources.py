import json
import pathlib

from ted_sws.metadata_normaliser.entrypoints.generate_mapping_resources import generate_mapping_files
from tests import TEST_DATA_PATH
from tests.fakes.fake_triple_store import FakeTripleStore


def test_generate_mapping_resources(tmp_path):
    queries_folder_path = TEST_DATA_PATH / "sparql_queries"
    output_folder_path = tmp_path
    generate_mapping_files(triple_store=FakeTripleStore(), queries_folder_path=queries_folder_path,
                           output_folder_path=output_folder_path)
    generated_file_paths = list(pathlib.Path(output_folder_path).rglob("*.json"))

    assert len(generated_file_paths) == 1
    assert "buyer_legal_type" == generated_file_paths[0].stem
    assert ".json" in str(generated_file_paths[0])

    generated_file_content = json.loads(pathlib.Path(output_folder_path / "buyer_legal_type.json").read_bytes())

    assert isinstance(generated_file_content, dict)
    assert "results" in generated_file_content.keys()
    assert generated_file_content["results"] == "awesome results"
