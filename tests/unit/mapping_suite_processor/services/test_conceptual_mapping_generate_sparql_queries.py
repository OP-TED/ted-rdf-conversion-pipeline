import shutil
import tempfile
from pathlib import Path

from ted_sws.mapping_suite_processor.entrypoints.cli.cmd_sparql_generator import DEFAULT_OUTPUT_SPARQL_QUERIES_FOLDER
from ted_sws.mapping_suite_processor.services.conceptual_mapping_generate_sparql_queries import \
    mapping_suite_processor_generate_sparql_queries
from ted_sws.mapping_suite_processor.entrypoints.cli import CONCEPTUAL_MAPPINGS_FILE_TEMPLATE


def test_mapping_suite_processor_generate_sparql_queries(caplog, fake_mapping_suite_id, file_system_repository_path):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_mapping_suite_path = Path(temp_folder)
        shutil.copytree(file_system_repository_path, temp_mapping_suite_path,
                        dirs_exist_ok=True)

        conceptual_mappings_file_path = Path(CONCEPTUAL_MAPPINGS_FILE_TEMPLATE.format(
            mappings_path=temp_mapping_suite_path,
            mapping_suite_id=fake_mapping_suite_id
        ))
        output_sparql_queries_folder_path = Path(DEFAULT_OUTPUT_SPARQL_QUERIES_FOLDER.format(
            mappings_path=temp_mapping_suite_path,
            mapping_suite_id=fake_mapping_suite_id
        ))
        mapping_suite_processor_generate_sparql_queries(
            conceptual_mappings_file_path=conceptual_mappings_file_path,
            output_sparql_queries_folder_path=output_sparql_queries_folder_path
        )
        assert output_sparql_queries_folder_path.is_dir()
        assert any(output_sparql_queries_folder_path.iterdir())
        assert "ERROR" not in caplog.text

        mapping_suite_processor_generate_sparql_queries(
            conceptual_mappings_file_path=conceptual_mappings_file_path,
            output_sparql_queries_folder_path=output_sparql_queries_folder_path,
            prefixes_definitions={
                "test": "https://test"
            }
        )
        assert output_sparql_queries_folder_path.is_dir()
        assert any(output_sparql_queries_folder_path.iterdir())
        assert "ERROR" in caplog.text
        assert "is not defined" in caplog.text