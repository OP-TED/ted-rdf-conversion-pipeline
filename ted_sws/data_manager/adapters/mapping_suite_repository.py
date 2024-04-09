import json
import os
import pathlib
import shutil
from datetime import datetime
from typing import Iterator, List, Optional

from pymongo import MongoClient

from ted_sws import config
from ted_sws.core.model.transform import MappingSuite, FileResource, TransformationRuleSet, SHACLTestSuite, \
    SPARQLTestSuite, MetadataConstraints, TransformationTestData, MappingSuiteType, \
    MetadataConstraintsStandardForm, MetadataConstraintsEform
from ted_sws.data_manager.adapters import inject_date_string_fields, remove_date_string_fields
from ted_sws.data_manager.adapters.repository_abc import MappingSuiteRepositoryABC

MS_METADATA_FILE_NAME = "metadata.json"
MS_TRANSFORM_FOLDER_NAME = "transformation"
MS_MAPPINGS_FOLDER_NAME = "mappings"
MS_RESOURCES_FOLDER_NAME = "resources"
MS_VALIDATE_FOLDER_NAME = "validation"
MS_SHACL_FOLDER_NAME = "shacl"
MS_SPARQL_FOLDER_NAME = "sparql"
MS_TEST_DATA_FOLDER_NAME = "test_data"
MS_CONCEPTUAL_MAPPING_FILE_NAME = "conceptual_mappings.xlsx"
MS_OUTPUT_FOLDER_NAME = "output"
MS_TEST_SUITE_REPORT = "test_suite_report"
MS_CREATED_AT_KEY = "created_at"
MONGODB_COLLECTION_ID = "_id"
MS_METADATA_IDENTIFIER_KEY = 'identifier'
MS_STANDARD_METADATA_VERSION_KEY = 'version'
MS_EFORMS_METADATA_VERSION_KEY = 'mapping_version'
MS_METADATA_CONSTRAINTS_KEY = 'metadata_constraints'
MS_CONSTRAINTS_KEY = 'constraints'
MS_TITLE_KEY = 'title'
MS_HASH_DIGEST_KEY = 'mapping_suite_hash_digest'
MS_MAPPING_TYPE_KEY = 'mapping_type'
MS_ONTOLOGY_VERSION_KEY = 'ontology_version'


class MappingSuiteRepositoryMongoDB(MappingSuiteRepositoryABC):
    """
       This repository is intended for storing MappingSuite objects in MongoDB.
    """

    _collection_name = "mapping_suite_collection"

    def __init__(self, mongodb_client: MongoClient, database_name: str = None):
        """

        :param mongodb_client:
        :param database_name:
        """
        mongodb_client = mongodb_client
        self._database_name = database_name or config.MONGO_DB_AGGREGATES_DATABASE_NAME
        notice_db = mongodb_client[self._database_name]
        self.collection = notice_db[self._collection_name]

    def _create_dict_from_mapping_suite(self, mapping_suite: MappingSuite) -> dict:
        """
            This method create a dict from mapping suite object.
        :param mapping_suite:
        :return:
        """
        mapping_suite_dict = mapping_suite.dict()
        mapping_suite_dict[MONGODB_COLLECTION_ID] = mapping_suite.get_mongodb_id()
        mapping_suite_dict[MS_CREATED_AT_KEY] = datetime.fromisoformat(mapping_suite_dict[MS_CREATED_AT_KEY])
        inject_date_string_fields(data=mapping_suite_dict, date_field_name=MS_CREATED_AT_KEY)
        return mapping_suite_dict

    def _create_mapping_suite_from_dict(self, mapping_suite_dict: dict) -> Optional[MappingSuite]:
        """
            This method create a mapping suite object from a dictionary.
        :param mapping_suite_dict:
        :return:
        """
        if mapping_suite_dict:
            mapping_suite_dict.pop(MONGODB_COLLECTION_ID, None)
            mapping_suite_dict[MS_CREATED_AT_KEY] = mapping_suite_dict[MS_CREATED_AT_KEY].isoformat()
            remove_date_string_fields(data=mapping_suite_dict, date_field_name=MS_CREATED_AT_KEY)
            return MappingSuite(**mapping_suite_dict)
        return None

    def add(self, mapping_suite: MappingSuite):
        """
            This method allows you to add MappingSuite objects to the repository.
        :param mapping_suite:
        :return:
        """
        mapping_suite_dict = self._create_dict_from_mapping_suite(mapping_suite=mapping_suite)
        mapping_suite_exist = self.collection.find_one(
            {MONGODB_COLLECTION_ID: mapping_suite_dict[MONGODB_COLLECTION_ID]})
        if mapping_suite_exist is None:
            self.collection.insert_one(mapping_suite_dict)

    def update(self, mapping_suite: MappingSuite):
        """
            This method allows you to update MappingSuite objects to the repository
        :param mapping_suite:
        :return:
        """
        mapping_suite_dict = self._create_dict_from_mapping_suite(mapping_suite=mapping_suite)
        self.collection.update_one({MONGODB_COLLECTION_ID: mapping_suite_dict[MONGODB_COLLECTION_ID]},
                                   {"$set": mapping_suite_dict})

    def get(self, reference) -> MappingSuite:
        """
            This method allows a MappingSuite to be obtained based on an identification reference.
        :param reference:
        :return: MappingSuite
        """
        result_dict = self.collection.find_one({MONGODB_COLLECTION_ID: reference})
        return self._create_mapping_suite_from_dict(mapping_suite_dict=result_dict)

    def list(self) -> Iterator[MappingSuite]:
        """
            This method allows all records to be retrieved from the repository.
        :return: list of MappingSuites
        """
        for result_dict in self.collection.find():
            yield self._create_mapping_suite_from_dict(mapping_suite_dict=result_dict)


class MappingSuiteRepositoryInFileSystem(MappingSuiteRepositoryABC):
    """
           This repository is intended for storing MappingSuite objects in FileSystem.
    """

    def __init__(self, repository_path: pathlib.Path):
        """

        :param repository_path:
        """
        self.repository_path = repository_path
        self.repository_path.mkdir(parents=True, exist_ok=True)

    def _read_package_metadata(self, package_path: pathlib.Path) -> dict:
        """
            This method allows reading the metadata of a packet.
        :param package_path:
        :return:
        """
        package_metadata_path = package_path / MS_METADATA_FILE_NAME
        package_metadata_content = package_metadata_path.read_text(encoding="utf-8")
        package_metadata = json.loads(package_metadata_content)
        return package_metadata

    def _read_transformation_rule_set(self, package_path: pathlib.Path) -> TransformationRuleSet:
        """
            This method allows you to read the transformation rules in a package.
        :param package_path:
        :return:
        """
        mappings_path = package_path / MS_TRANSFORM_FOLDER_NAME / MS_MAPPINGS_FOLDER_NAME
        resources_path = package_path / MS_TRANSFORM_FOLDER_NAME / MS_RESOURCES_FOLDER_NAME
        resources = self._read_file_resources(path=resources_path)
        rml_mapping_rules = self._read_file_resources(path=mappings_path)
        return TransformationRuleSet(resources=resources, rml_mapping_rules=rml_mapping_rules)

    def _read_shacl_test_suites(self, package_path: pathlib.Path) -> List[SHACLTestSuite]:
        """
            This method allows you to read shacl test suites from a package.
        :param package_path:
        :return:
        """
        validate_path = package_path / MS_VALIDATE_FOLDER_NAME
        shacl_path = validate_path / MS_SHACL_FOLDER_NAME
        shacl_test_suite_paths = [x for x in shacl_path.iterdir() if x.is_dir()]
        return [SHACLTestSuite(identifier=shacl_test_suite_path.name,
                               shacl_tests=self._read_file_resources(path=shacl_test_suite_path))
                for shacl_test_suite_path in shacl_test_suite_paths]

    def _read_sparql_test_suites(self, package_path: pathlib.Path) -> List[SPARQLTestSuite]:
        """
            This method allows you to read sparql test suites from a package.
        :param package_path:
        :return:
        """
        validate_path = package_path / MS_VALIDATE_FOLDER_NAME
        sparql_path = validate_path / MS_SPARQL_FOLDER_NAME
        sparql_test_suite_paths = [x for x in sparql_path.iterdir() if x.is_dir()]
        return [SPARQLTestSuite(identifier=sparql_test_suite_path.name,
                                sparql_tests=self._read_file_resources(path=sparql_test_suite_path))
                for sparql_test_suite_path in sparql_test_suite_paths]

    def _write_package_metadata(self, mapping_suite: MappingSuite):
        """
            This method creates the metadata of a package based on the metadata in the mapping_suite.
        :param mapping_suite:
        :return:
        """
        package_path = self.repository_path / mapping_suite.identifier
        package_path.mkdir(parents=True, exist_ok=True)
        metadata_path = package_path / MS_METADATA_FILE_NAME
        package_metadata = mapping_suite.dict()
        [package_metadata.pop(key, None) for key in
         ["transformation_rule_set", "shacl_test_suites", "sparql_test_suites"]]
        with metadata_path.open("w", encoding="utf-8") as f:
            f.write(json.dumps(package_metadata))

    def _write_file_resources(self, file_resources: List[FileResource], path: pathlib.Path):
        """
            This method allows you to write a list of file-type resources to a specific location.
        :param file_resources:
        :param path:
        :return:
        """
        for file_resource in file_resources:
            file_resource_path = path / file_resource.file_name
            with file_resource_path.open("w", encoding="utf-8") as f:
                f.write(file_resource.file_content)

    @classmethod
    def read_flat_file_resources(cls, path: pathlib.Path, file_resources=None, extension=None, with_content=True) -> \
            List[FileResource]:
        """
        This method reads a folder (with nested-tree structure) of resources and returns a flat list of file-type
        resources from all beyond levels.
        Used for folders that contains files with unique names, but grouped into sub-folders.
        :param with_content:
        :param extension:
        :param path:
        :param file_resources:
        :return:
        """
        if file_resources is None:
            file_resources: List[FileResource] = []

        for root, dirs, files in os.walk(path):
            file_parents = list(
                map(lambda path_value: str(path_value), pathlib.Path(os.path.relpath(root, path)).parts))
            for f in files:
                file_extension = pathlib.Path(f).suffix
                if extension is not None and file_extension != extension:
                    continue
                file_path = pathlib.Path(os.path.join(root, f))
                file_resource = FileResource(file_name=file_path.name,
                                             file_content=file_path.read_text(
                                                 encoding="utf-8") if with_content else "",
                                             original_name=file_path.name,
                                             parents=file_parents)
                file_resources.append(file_resource)

        return file_resources

    @classmethod
    def _read_file_resources(cls, path: pathlib.Path) -> List[FileResource]:
        """
            This method reads a list of file-type resources that are in a specific location.
        :param path:
        :return:
        """
        files = [file for file in path.iterdir() if file.is_file()]
        return [FileResource(file_name=file.name,
                             file_content=file.read_text(encoding="utf-8"),
                             original_name=file.name)
                for file in files]

    def _write_package_transform_rules(self, mapping_suite: MappingSuite):
        """
            This method creates the transformation rules within the package.
        :param mapping_suite:
        :return:
        """
        package_path = self.repository_path / mapping_suite.identifier
        transform_path = package_path / MS_TRANSFORM_FOLDER_NAME
        mappings_path = transform_path / MS_MAPPINGS_FOLDER_NAME
        resources_path = transform_path / MS_RESOURCES_FOLDER_NAME
        mappings_path.mkdir(parents=True, exist_ok=True)
        resources_path.mkdir(parents=True, exist_ok=True)
        self._write_file_resources(file_resources=mapping_suite.transformation_rule_set.rml_mapping_rules,
                                   path=mappings_path
                                   )
        self._write_file_resources(file_resources=mapping_suite.transformation_rule_set.resources,
                                   path=resources_path
                                   )

    def _write_package_validation_rules(self, mapping_suite: MappingSuite):
        """
            This method creates the validation rules within the package.
        :param mapping_suite:
        :return:
        """
        package_path = self.repository_path / mapping_suite.identifier
        validate_path = package_path / MS_VALIDATE_FOLDER_NAME
        sparql_path = validate_path / MS_SPARQL_FOLDER_NAME
        shacl_path = validate_path / MS_SHACL_FOLDER_NAME
        sparql_path.mkdir(parents=True, exist_ok=True)
        shacl_path.mkdir(parents=True, exist_ok=True)
        shacl_test_suites = mapping_suite.shacl_test_suites
        for shacl_test_suite in shacl_test_suites:
            shacl_test_suite_path = shacl_path / shacl_test_suite.identifier
            shacl_test_suite_path.mkdir(parents=True, exist_ok=True)
            self._write_file_resources(file_resources=shacl_test_suite.shacl_tests,
                                       path=shacl_test_suite_path
                                       )

        sparql_test_suites = mapping_suite.sparql_test_suites
        for sparql_test_suite in sparql_test_suites:
            sparql_test_suite_path = sparql_path / sparql_test_suite.identifier
            sparql_test_suite_path.mkdir(parents=True, exist_ok=True)
            self._write_file_resources(file_resources=sparql_test_suite.sparql_tests,
                                       path=sparql_test_suite_path
                                       )

    def _write_test_data_package(self, mapping_suite: MappingSuite):
        """
            This method writes the test data to a dedicated folder in the package.
        :param mapping_suite:
        :return:
        """
        package_path = self.repository_path / mapping_suite.identifier
        test_data_path = package_path / MS_TEST_DATA_FOLDER_NAME
        test_data_path.mkdir(parents=True, exist_ok=True)
        self._write_file_resources(file_resources=mapping_suite.transformation_test_data.test_data,
                                   path=test_data_path
                                   )

    def _read_test_data_package(self, package_path: pathlib.Path) -> TransformationTestData:
        """
            This method reads the test data from the package.
        :param package_path:
        :return:
        """
        test_data_path = package_path / MS_TEST_DATA_FOLDER_NAME
        test_data = self.read_flat_file_resources(path=test_data_path)
        return TransformationTestData(test_data=test_data)

    def _write_mapping_suite_package(self, mapping_suite: MappingSuite):
        """
            This method creates a package based on data from mapping_suite.
        :param mapping_suite:
        :return:
        """
        self._write_package_metadata(mapping_suite=mapping_suite)
        self._write_package_transform_rules(mapping_suite=mapping_suite)
        self._write_package_validation_rules(mapping_suite=mapping_suite)
        self._write_test_data_package(mapping_suite=mapping_suite)

    def _read_mapping_suite_package(self, mapping_suite_identifier: str) -> Optional[MappingSuite]:
        """
            This method reads a package and initializes a MappingSuite object.
        :param mapping_suite_identifier:
        :return:
        """
        package_path = self.repository_path / mapping_suite_identifier
        if package_path.is_dir():
            package_metadata = self._read_package_metadata(package_path)
            if MS_MAPPING_TYPE_KEY in package_metadata and package_metadata[
                MS_MAPPING_TYPE_KEY] == MappingSuiteType.ELECTRONIC_FORMS:
                package_metadata[MS_METADATA_CONSTRAINTS_KEY] = MetadataConstraints(
                    constraints=MetadataConstraintsEform(
                        **package_metadata[MS_METADATA_CONSTRAINTS_KEY][MS_CONSTRAINTS_KEY]))
            else:
                package_metadata[MS_METADATA_CONSTRAINTS_KEY] = MetadataConstraints(
                    constraints=MetadataConstraintsStandardForm(
                        **package_metadata[MS_METADATA_CONSTRAINTS_KEY][MS_CONSTRAINTS_KEY]))
            mapping_suite = MappingSuite(
                metadata_constraints=package_metadata[MS_METADATA_CONSTRAINTS_KEY],
                created_at=package_metadata[MS_CREATED_AT_KEY],
                title=package_metadata[MS_TITLE_KEY],
                ontology_version=package_metadata[MS_ONTOLOGY_VERSION_KEY],
                mapping_suite_hash_digest=package_metadata[MS_HASH_DIGEST_KEY],
                mapping_type=package_metadata[
                    MS_MAPPING_TYPE_KEY] if MS_MAPPING_TYPE_KEY in package_metadata else MappingSuiteType.STANDARD_FORMS,
                version=package_metadata[
                    MS_STANDARD_METADATA_VERSION_KEY] if MS_STANDARD_METADATA_VERSION_KEY in package_metadata else \
                    package_metadata[MS_EFORMS_METADATA_VERSION_KEY],
                identifier=package_metadata[
                    MS_METADATA_IDENTIFIER_KEY] if MS_METADATA_IDENTIFIER_KEY in package_metadata else mapping_suite_identifier,
                transformation_rule_set=self._read_transformation_rule_set(package_path),
                shacl_test_suites=self._read_shacl_test_suites(package_path),
                sparql_test_suites=self._read_sparql_test_suites(package_path),
                transformation_test_data=self._read_test_data_package(package_path)
            )
            return mapping_suite
        return None

    @classmethod
    def mapping_suite_notice_path_by_group_depth(cls, path: pathlib.Path, group_depth: int = 0) -> pathlib.Path:
        return pathlib.Path(*path.parts[:(-group_depth if group_depth else None)]) if path else None

    def add(self, mapping_suite: MappingSuite):
        """
            This method allows you to add MappingSuite objects to the repository.
        :param mapping_suite:
        :return:
        """
        self._write_mapping_suite_package(mapping_suite=mapping_suite)

    def update(self, mapping_suite: MappingSuite):
        """
            This method allows you to update MappingSuite objects to the repository
        :param mapping_suite:
        :return:
        """
        package_path = self.repository_path / mapping_suite.identifier
        if package_path.is_dir():
            self._write_mapping_suite_package(mapping_suite=mapping_suite)

    def get(self, reference) -> MappingSuite:
        """
            This method allows a MappingSuite to be obtained based on an identification reference.
        :param reference:
        :return: MappingSuite
        """
        return self._read_mapping_suite_package(mapping_suite_identifier=reference)

    def list(self) -> Iterator[MappingSuite]:
        """
            This method allows all records to be retrieved from the repository.
        :return: list of MappingSuites
        """
        package_paths = [x for x in self.repository_path.iterdir() if x.is_dir()]
        for package_path in package_paths:
            yield self.get(reference=package_path.name)

    def clear_repository(self):
        """
            This method allows you to clean the repository.
        :return:
        """
        shutil.rmtree(self.repository_path)
