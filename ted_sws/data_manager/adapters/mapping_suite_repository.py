import json
import pathlib
from typing import Iterator, List

from pymongo import MongoClient

from ted_sws.domain.adapters.repository_abc import MappingSuiteRepositoryABC
from ted_sws.domain.model.transform import MappingSuite, FileResource


class MappingSuiteRepositoryMongoDB(MappingSuiteRepositoryABC):
    """
       This repository is intended for storing MappingSuite objects in MongoDB.
    """

    _collection_name = "mapping_suite_collection"
    _database_name = "mapping_suite_db"

    def __init__(self, mongodb_client: MongoClient, database_name: str = None):
        """

        :param mongodb_client:
        :param database_name:
        """
        mongodb_client = mongodb_client
        notice_db = mongodb_client[database_name if database_name else self._database_name]
        self.collection = notice_db[self._collection_name]

    def add(self, mapping_suite: MappingSuite):
        """
            This method allows you to add MappingSuite objects to the repository.
        :param mapping_suite:
        :return:
        """
        mapping_suite_dict = mapping_suite.dict()
        mapping_suite_dict["_id"] = mapping_suite_dict["identifier"]
        self.collection.insert_one(mapping_suite_dict)

    def update(self, mapping_suite: MappingSuite):
        """
            This method allows you to update MappingSuite objects to the repository
        :param mapping_suite:
        :return:
        """
        mapping_suite_dict = mapping_suite.dict()
        mapping_suite_dict["_id"] = mapping_suite_dict["identifier"]
        self.collection.update_one({'_id': mapping_suite_dict["_id"]}, {"$set": mapping_suite_dict})

    def get(self, reference) -> MappingSuite:
        """
            This method allows a MappingSuite to be obtained based on an identification reference.
        :param reference:
        :return: MappingSuite
        """
        result_dict = self.collection.find_one({"identifier": reference})
        return MappingSuite(**result_dict) if result_dict else None

    def list(self) -> Iterator[MappingSuite]:
        """
            This method allows all records to be retrieved from the repository.
        :return: list of MappingSuites
        """
        for result_dict in self.collection.find():
            yield MappingSuite(**result_dict)


class MappingSuiteRepositoryInFileSystem(MappingSuiteRepositoryABC):
    """
           This repository is intended for storing MappingSuite objects in FileSystem.
    """

    def __init__(self, repository_path: pathlib.Path):
        """

        :param repository_path:
        """
        self.repository_path = repository_path

    def _read_package_metadate(self, package_metadata_path: pathlib.Path) -> dict:
        pass

    def _create_package_metadata(self, mapping_suite: MappingSuite):
        package_path = self.repository_path / mapping_suite.identifier
        package_path.mkdir(parents=True, exist_ok=True)
        metadata_path = package_path / "metadata.json"
        package_metadata = dict()
        package_metadata['title'] = mapping_suite.title
        package_metadata['created_at'] = mapping_suite.created_at
        package_metadata['identifier'] = mapping_suite.identifier
        package_metadata['version'] = mapping_suite.version
        package_metadata['metadata_constraints'] = mapping_suite.metadata_constraints.dict()
        with metadata_path.open("w", encoding="utf-8") as f:
            f.write(json.dumps(package_metadata))

    def _write_file_resources(self, file_resources: List[FileResource], path: pathlib.Path):
        for file_resource in file_resources:
            file_resource_path = path / file_resource.file_name
            with file_resource_path.open("w", encoding="utf-8") as f:
                f.write(file_resource.file_content)

    def _read_file_resources(self, path: pathlib.Path) -> List[FileResource]:
        files = [file for file in path.glob('**/*') if file.is_file()]
        return [FileResource(file_name=file.name,
                             file_content=file.read_text(encoding="utf-8"))
                for file in files]

    def _create_package_transform_rules(self, mapping_suite: MappingSuite):
        package_path = self.repository_path / mapping_suite.identifier
        transform_path = package_path / "transform"
        mappings_path = transform_path / "mappings"
        resources_path = transform_path / "resource"
        mappings_path.mkdir(parents=True, exist_ok=True)
        resources_path.mkdir(parents=True, exist_ok=True)
        self._write_file_resources(file_resources=mapping_suite.transformation_rule_set.rml_mapping_rules,
                                   path=mappings_path
                                   )
        self._write_file_resources(file_resources=mapping_suite.transformation_rule_set.resources,
                                   path=resources_path
                                   )

    def _create_package_validation_rules(self, mapping_suite: MappingSuite):
        package_path = self.repository_path / mapping_suite.identifier
        validate_path = package_path / "validate"
        sparql_path = validate_path / "sparql"
        shacl_path = validate_path / "shacl"
        sparql_path.mkdir(parents=True, exist_ok=True)
        shacl_path.mkdir(parents=True, exist_ok=True)
        shacl_test_suites = mapping_suite.shacl_test_suites
        shacl_test_suite_path_counter = 0
        for shacl_test_suite in shacl_test_suites:
            shacl_test_suite_path = shacl_path / f"shacl_test_suite_{shacl_test_suite_path_counter}"
            shacl_test_suite_path.mkdir(parents=True, exist_ok=True)
            self._write_file_resources(file_resources=shacl_test_suite.shacl_tests,
                                       path=shacl_test_suite_path
                                       )
            shacl_test_suite_path_counter += 1

        sparql_test_suites = mapping_suite.sparql_test_suites
        sparql_test_suite_path_counter = 0
        for sparql_test_suite in sparql_test_suites:
            sparql_test_suite_path = sparql_path / f"sparql_test_suite_{sparql_test_suite_path_counter}"
            sparql_test_suite_path.mkdir(parents=True, exist_ok=True)
            self._write_file_resources(file_resources=sparql_test_suite.sparql_tests,
                                       path=sparql_test_suite_path
                                       )
            sparql_test_suite_path_counter += 1

    def _create_mapping_suite_package(self, mapping_suite: MappingSuite):
        """

        :param mapping_suite:
        :return:
        """
        self._create_package_metadata(mapping_suite=mapping_suite)
        self._create_package_transform_rules(mapping_suite=mapping_suite)
        self._create_package_validation_rules(mapping_suite=mapping_suite)

    def add(self, mapping_suite: MappingSuite):
        """
            This method allows you to add MappingSuite objects to the repository.
        :param mapping_suite:
        :return:
        """
        self._create_mapping_suite_package(mapping_suite=mapping_suite)

    def update(self, mapping_suite: MappingSuite):
        """
            This method allows you to update MappingSuite objects to the repository
        :param mapping_suite:
        :return:
        """
        self._create_mapping_suite_package(mapping_suite=mapping_suite)

    def get(self, reference) -> MappingSuite:
        """
            This method allows a MappingSuite to be obtained based on an identification reference.
        :param reference:
        :return: MappingSuite
        """
        pass

    def list(self) -> Iterator[MappingSuite]:
        """
            This method allows all records to be retrieved from the repository.
        :return: list of MappingSuites
        """
        pass
