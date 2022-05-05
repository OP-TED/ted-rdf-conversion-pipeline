from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem, \
    MappingSuiteRepositoryMongoDB
from ted_sws.mapping_suite_processor.services.conceptual_mapping_processor import CONCEPTUAL_MAPPINGS_ASSERTIONS, \
    mapping_suite_processor_expand_package, mapping_suite_processor_load_package_in_mongo_db
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
        sparql_packages = set(map(lambda x: x.identifier, mapping_suite.sparql_test_suites))
        assert CONCEPTUAL_MAPPINGS_ASSERTIONS in sparql_packages
        for sparql_test_suite in mapping_suite.sparql_test_suites:
            if sparql_test_suite.identifier == CONCEPTUAL_MAPPINGS_ASSERTIONS:
                assert len(sparql_test_suite.sparql_tests) == 66

        assert mapping_suite.metadata_constraints
        assert mapping_suite.title == "sample_title"
        assert mapping_suite.identifier == "test_package"
        assert mapping_suite.version == "0.0.1"
        assert mapping_suite.ontology_version == "3.0.0.alpha"
        assert 13 in set(mapping_suite.metadata_constraints.constraints["eforms_subtype"])
        assert "R2.0.9.S04.E06" not in set(mapping_suite.metadata_constraints.constraints["min_xsd_version"])

        assert mapping_suite.shacl_test_suites
        assert len(mapping_suite.shacl_test_suites) == 1
        assert mapping_suite.transformation_rule_set.resources
        assert len(mapping_suite.transformation_rule_set.resources) == 3

        assert mapping_suite.sparql_test_suites
        assert len(mapping_suite.sparql_test_suites) == 2
        assert "business_queries" in set(map(lambda x: x.identifier, mapping_suite.sparql_test_suites))
        assert "cm_assertions" in set(map(lambda x: x.identifier, mapping_suite.sparql_test_suites))
        assert "not_cm_assertions" not in set(map(lambda x: x.identifier, mapping_suite.sparql_test_suites))

        tmp_prod_archive_path = tmp_mapping_suite_package_path.parent / f"{tmp_mapping_suite_package_path.stem}-prod.zip"
        tmp_demo_archive_path = tmp_mapping_suite_package_path.parent / f"{tmp_mapping_suite_package_path.stem}-demo.zip"

        assert tmp_prod_archive_path.is_file()
        assert tmp_demo_archive_path.is_file()

        tmp_prod_archive_path.unlink()
        tmp_demo_archive_path.unlink()

        assert not tmp_prod_archive_path.is_file()
        assert not tmp_demo_archive_path.is_file()


def test_mapping_suite_processor_upload_in_mongodb(file_system_repository_path, mongodb_client):
    with temporary_copy(file_system_repository_path) as tmp_mapping_suite_package_path:
        mapping_suite_package_path = tmp_mapping_suite_package_path / "test_package"
        mapping_suite_processor_expand_package(mapping_suite_package_path=mapping_suite_package_path)
        mapping_suite_processor_load_package_in_mongo_db(mapping_suite_package_path=mapping_suite_package_path,
                                                          mongodb_client=mongodb_client)
        mapping_suite_repository = MappingSuiteRepositoryInFileSystem(
            repository_path=tmp_mapping_suite_package_path)
        mapping_suite = mapping_suite_repository.get(reference=mapping_suite_package_path.name)
        assert mapping_suite
        mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
        mapping_suite = mapping_suite_repository.get(reference=mapping_suite_package_path.name)
        assert mapping_suite

    mongodb_client.drop_database(MappingSuiteRepositoryMongoDB._database_name)
