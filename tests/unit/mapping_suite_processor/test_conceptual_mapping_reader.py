from pathlib import Path

from ted_sws.mapping_suite_processor.services.conceptual_mapping_reader import mapping_suite_read_conceptual_mapping, \
    conceptual_mapping_read_list_from_pd_value
from tests import temporary_copy


def test__read_list_from_pd_value():
    assert conceptual_mapping_read_list_from_pd_value(None) == []


def test_mapping_suite_read_conceptual_mapping(file_system_repository_path, mongodb_client):
    with temporary_copy(file_system_repository_path / "test_package") as tmp_mapping_suite_package_path:
        conceptual_mappings_folder = Path(tmp_mapping_suite_package_path) / "transformation"

        conceptual_mapping = mapping_suite_read_conceptual_mapping(
            conceptual_mappings_folder / "conceptual_mappings.xlsx")

        assert conceptual_mapping

        conceptual_mapping = mapping_suite_read_conceptual_mapping(
            conceptual_mappings_folder / "non_existing_conceptual_mappings.xlsx")

        assert not conceptual_mapping
