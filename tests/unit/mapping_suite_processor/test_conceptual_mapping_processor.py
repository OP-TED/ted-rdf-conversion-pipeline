from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.mapping_suite_processor.services.conceptual_mapping_processor import CONCEPTUAL_MAPPINGS_ASSERTIONS, \
    mapping_suite_processor_expand_package
from tests import temporary_copy


def test_mapping_suite_processor_expand_package(file_system_repository_path):
    mapping_suite_package_path = file_system_repository_path / "test_package"
    with temporary_copy(mapping_suite_package_path) as tmp_mapping_suite_package_path:
        mapping_suite_processor_expand_package(mapping_suite_package_path=tmp_mapping_suite_package_path)
        mapping_suite_repository = MappingSuiteRepositoryInFileSystem(
            repository_path=tmp_mapping_suite_package_path.parent)
        mapping_suite = mapping_suite_repository.get(reference="test_package")
        assert mapping_suite
        assert mapping_suite.sparql_test_suites
        assert len(mapping_suite.sparql_test_suites) == 2
        sparql_packages = set(map(lambda x: x.identifier, mapping_suite.sparql_test_suites))
        assert "sparql_test_suite_0" in sparql_packages
        assert CONCEPTUAL_MAPPINGS_ASSERTIONS in sparql_packages
        for sparql_test_suite in mapping_suite.sparql_test_suites:
            if sparql_test_suite.identifier == CONCEPTUAL_MAPPINGS_ASSERTIONS:
                assert len(sparql_test_suite.sparql_tests) == 66

        assert mapping_suite.metadata_constraints
        assert mapping_suite.title == "sample_title"
        assert mapping_suite.identifier == "mapping_id"
        assert mapping_suite.version == "0.0.1"
        assert mapping_suite.ontology_version == "3.0.0.alpha"
        assert "F03" in set(mapping_suite.metadata_constraints.constraints["form_number"])
        assert "F04" not in set(mapping_suite.metadata_constraints.constraints["form_number"])

