import json
import os
import pathlib
import shutil
from typing import Iterator, List, Optional

from pymongo import MongoClient

from mapping_suite_sdk.core.adapters.repository import MongoDBRepository, ModelNotFoundError

# WORKAROUND: Disable __del__ in MSSDK's MongoDBRepository to prevent premature client closure
# The MSSDK MongoDBRepository closes the MongoClient in __del__, but it doesn't own the client.
# When the repository is garbage collected, it closes the shared client unexpectedly.
if hasattr(MongoDBRepository, '__del__'):
    delattr(MongoDBRepository, '__del__')
from mapping_suite_sdk.mapping_package_v1.models import MappingPackageV1
from mapping_suite_sdk.mapping_package_v2.models import MappingPackageV2
from mapping_suite_sdk.mapping_package_v3.models import MappingPackageV3
from mapping_suite_sdk.mapping_package_v3.models.mapping_package_v3_lightweight import MappingPackageV3Lightweight

from src.ted_sws import config
from src.ted_sws.core.model.transform import MappingPackage, FileResource, TransformationRuleSet, SHACLTestSuite, \
    SPARQLTestSuite, MetadataConstraints, TransformationTestData, MappingPackageType, \
    MetadataConstraintsStandardForm, MetadataConstraintsEform
from src.ted_sws.data_manager.adapters.repository_abc import MappingPackageRepositoryABC

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
MS_METADATA_CONSTRAINTS_START_DATE_KEY = 'start_date'
MS_METADATA_CONSTRAINTS_END_DATE_KEY = 'end_date'
MS_CONSTRAINTS_KEY = 'constraints'
MS_TITLE_KEY = 'title'
MS_HASH_DIGEST_KEY = 'mapping_suite_hash_digest'
MS_MAPPING_TYPE_KEY = 'mapping_type'
MS_ONTOLOGY_VERSION_KEY = 'ontology_version'


class MappingPackageRepositoryMongoDB(MappingPackageRepositoryABC):
    """This repository is intended for storing MappingPackage objects in MongoDB with MSSDK models.

    Provides unified interface for CRUD operations on mapping packages
    of different versions (V1, V2, V3, V3Lightweight).
    """

    _collection_name = "mapping_package_collection"

    def __init__(self, mongodb_client: MongoClient, database_name: str = None):
        """Initialize the repository.

        Args:
            mongodb_client: MongoDB client instance
            database_name: Database name (defaults to config value)
        """
        self.database_name = database_name or config.MONGO_DB_AGGREGATES_DATABASE_NAME
        self.mongodb_client = mongodb_client

        # Repositories for each package type
        self._repo_v1 = MongoDBRepository(
            model_class=MappingPackageV1,
            mongo_client=mongodb_client,
            database_name=self.database_name,
            collection_name=self._collection_name
        )
        self._repo_v2 = MongoDBRepository(
            model_class=MappingPackageV2,
            mongo_client=mongodb_client,
            database_name=self.database_name,
            collection_name=self._collection_name
        )
        self._repo_v3 = MongoDBRepository(
            model_class=MappingPackageV3,
            mongo_client=mongodb_client,
            database_name=self.database_name,
            collection_name=self._collection_name
        )
        self._repo_v3_lightweight = MongoDBRepository(
            model_class=MappingPackageV3Lightweight,
            mongo_client=mongodb_client,
            database_name=self.database_name,
            collection_name=self._collection_name
        )
        self._repo_legacy = MongoDBRepository(
            model_class=MappingPackage,
            mongo_client=mongodb_client,
            database_name=self.database_name,
            collection_name=self._collection_name
        )

    def _get_repository(self, package: MappingPackage) -> MongoDBRepository:
        """Get the appropriate repository based on package type."""
        if isinstance(package, MappingPackageV3Lightweight):
            return self._repo_v3_lightweight
        elif isinstance(package, MappingPackageV3):
            return self._repo_v3
        elif isinstance(package, MappingPackageV2):
            return self._repo_v2
        elif isinstance(package, MappingPackageV1):
            return self._repo_v1
        elif isinstance(package, MappingPackage):
            return self._repo_legacy
        else:
            raise ValueError(f"Unsupported package type: {type(package).__name__}")

    def get_repository_by_class(self, package_class):
        if package_class == MappingPackageV1:
            return self._repo_v1
        elif package_class == MappingPackageV2:
            return self._repo_v2
        elif package_class == MappingPackageV3:
            return self._repo_v3
        elif package_class == MappingPackageV3Lightweight:
            return self._repo_v3_lightweight
        elif package_class == MappingPackage:
            return self._repo_legacy
        else:
            raise ValueError(f"Unsupported package class: {package_class.__name__}")

    def add(self, mapping_package: MappingPackage) -> MappingPackage:
        """Save a mapping package to MongoDB.

        Args:
            mapping_package: The mapping package (legacy or MSSDK model)

        Returns:
            The saved package
        """
        repo = self._get_repository(mapping_package)
        return repo.create(mapping_package)

    def get(self, reference: str, package_class: type = MappingPackage) -> MappingPackage:
        """Retrieve a mapping package from MongoDB.

        Args:
            reference: The package identifier
            package_class: The expected package model class (defaults to MappingPackage)

        Returns:
            The retrieved package

        Raises:
            ModelNotFoundError: If package not found
        """
        repo = self.get_repository_by_class(package_class)
        return repo.read(reference)

    def update(self, mapping_package: MappingPackage) -> MappingPackage:
        """Update a mapping package in MongoDB.

        Args:
            mapping_package: The package to update

        Returns:
            The updated package
        """
        repo = self._get_repository(mapping_package)
        return repo.update(mapping_package)

    def delete(self, reference: str) -> None:
        """Delete a mapping package from MongoDB.

        Args:
            reference: The package identifier
        """
        db = self.mongodb_client[self.database_name]
        collection = db[self._collection_name]
        result = collection.delete_one({'_id': reference})
        if result.deleted_count < 1:
            raise ModelNotFoundError(f"Package with ID {reference} not found")

    def list(self, package_class: type = MappingPackage) -> List[MappingPackage]:
        """List mapping packages from MongoDB.

        Args:
            package_class: The package model class to retrieve (defaults to V2)

        Returns:
            List of packages
        """
        repo = self.get_repository_by_class(package_class)
        return repo.read_many()


# DEPRECATED - use MSSDK for reading and writing to FS, remove once all code especially tests are updated
class MappingPackageRepositoryInFileSystem(MappingPackageRepositoryABC):
    """
           This repository is intended for storing MappingPackage objects in FileSystem.
    """

    def __init__(self, repository_path: pathlib.Path):
        """

        :param repository_path:
        """
        self.repository_path = repository_path
        self.repository_path.mkdir(parents=True, exist_ok=True)

    def _preprocess_package_metadata(self, package_metadata: dict):
        """
            This method is adjusting the metadata structure to be fully compatible.
        :param package_metadata:
        :return:
        """
        if MS_METADATA_CONSTRAINTS_KEY in package_metadata:
            metadata_constraints = package_metadata[MS_METADATA_CONSTRAINTS_KEY]
            if MS_CONSTRAINTS_KEY in metadata_constraints:
                constraints = metadata_constraints[MS_CONSTRAINTS_KEY]
                if MS_METADATA_CONSTRAINTS_START_DATE_KEY in constraints:
                    start_date_value = constraints[MS_METADATA_CONSTRAINTS_START_DATE_KEY]
                    if start_date_value and not isinstance(start_date_value, list):
                        package_metadata[MS_METADATA_CONSTRAINTS_KEY][MS_CONSTRAINTS_KEY][
                            MS_METADATA_CONSTRAINTS_START_DATE_KEY] = [start_date_value]
                    end_date_value = constraints[MS_METADATA_CONSTRAINTS_END_DATE_KEY]
                    if end_date_value and not isinstance(end_date_value, list):
                        package_metadata[MS_METADATA_CONSTRAINTS_KEY][MS_CONSTRAINTS_KEY][
                            MS_METADATA_CONSTRAINTS_END_DATE_KEY] = [end_date_value]

    def _read_package_metadata(self, package_path: pathlib.Path) -> dict:
        """
            This method allows reading the metadata of a packet.
        :param package_path:
        :return:
        """
        package_metadata_path = package_path / MS_METADATA_FILE_NAME
        package_metadata_content = package_metadata_path.read_text(encoding="utf-8")
        package_metadata = json.loads(package_metadata_content)
        self._preprocess_package_metadata(package_metadata)
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

    def _write_package_metadata(self, mapping_package: MappingPackage):
        """
            This method creates the metadata of a package based on the metadata in the mapping_package.
        :param mapping_package:
        :return:
        """
        import base64

        def convert_for_json(obj):
            """Convert non-JSON-serializable objects (Path, bytes) to serializable form."""
            if isinstance(obj, pathlib.Path):
                return str(obj)
            elif isinstance(obj, bytes):
                # Convert bytes to base64 string for JSON serialization
                return base64.b64encode(obj).decode('utf-8')
            elif isinstance(obj, dict):
                return {k: convert_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_for_json(i) for i in obj]
            elif isinstance(obj, tuple):
                return tuple(convert_for_json(i) for i in obj)
            else:
                return obj

        package_path = self.repository_path / mapping_package.identifier
        package_path.mkdir(parents=True, exist_ok=True)
        metadata_path = package_path / MS_METADATA_FILE_NAME
        package_metadata = mapping_package.model_dump()
        # Exclude legacy fields (written separately) and MSSDK collection asset fields (contain file content)
        fields_to_exclude = [
            "transformation_rule_set", "shacl_test_suites", "sparql_test_suites",  # Legacy fields
            "technical_mapping_suite", "vocabulary_mapping_suite",  # MSSDK - written separately
            "conceptual_mapping_asset",  # MSSDK - bytes content (xlsx)
            "test_data_suites", "test_suites_sparql", "test_suites_shacl", "test_results",  # MSSDK test suites
        ]
        for key in fields_to_exclude:
            package_metadata.pop(key, None)
        package_metadata = convert_for_json(package_metadata)
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

    def _write_package_transform_rules(self, mapping_package: MappingPackage):
        """
            This method creates the transformation rules within the package.
        :param mapping_package:
        :return:
        """
        if mapping_package.transformation_rule_set is None:
            return
        package_path = self.repository_path / mapping_package.identifier
        transform_path = package_path / MS_TRANSFORM_FOLDER_NAME
        mappings_path = transform_path / MS_MAPPINGS_FOLDER_NAME
        resources_path = transform_path / MS_RESOURCES_FOLDER_NAME
        mappings_path.mkdir(parents=True, exist_ok=True)
        resources_path.mkdir(parents=True, exist_ok=True)
        self._write_file_resources(file_resources=mapping_package.transformation_rule_set.rml_mapping_rules,
                                   path=mappings_path
                                   )
        self._write_file_resources(file_resources=mapping_package.transformation_rule_set.resources,
                                   path=resources_path
                                   )

    def _write_package_validation_rules(self, mapping_package: MappingPackage):
        """
            This method creates the validation rules within the package.
        :param mapping_package:
        :return:
        """
        package_path = self.repository_path / mapping_package.identifier
        validate_path = package_path / MS_VALIDATE_FOLDER_NAME
        sparql_path = validate_path / MS_SPARQL_FOLDER_NAME
        shacl_path = validate_path / MS_SHACL_FOLDER_NAME
        sparql_path.mkdir(parents=True, exist_ok=True)
        shacl_path.mkdir(parents=True, exist_ok=True)
        shacl_test_suites = mapping_package.shacl_test_suites
        for shacl_test_suite in shacl_test_suites:
            shacl_test_suite_path = shacl_path / shacl_test_suite.identifier
            shacl_test_suite_path.mkdir(parents=True, exist_ok=True)
            self._write_file_resources(file_resources=shacl_test_suite.shacl_tests,
                                       path=shacl_test_suite_path
                                       )

        sparql_test_suites = mapping_package.sparql_test_suites
        for sparql_test_suite in sparql_test_suites:
            sparql_test_suite_path = sparql_path / sparql_test_suite.identifier
            sparql_test_suite_path.mkdir(parents=True, exist_ok=True)
            self._write_file_resources(file_resources=sparql_test_suite.sparql_tests,
                                       path=sparql_test_suite_path
                                       )

    def _write_test_data_package(self, mapping_package: MappingPackage):
        """
            This method writes the test data to a dedicated folder in the package.
        :param mapping_package:
        :return:
        """
        if mapping_package.transformation_test_data is None:
            return
        package_path = self.repository_path / mapping_package.identifier
        test_data_path = package_path / MS_TEST_DATA_FOLDER_NAME
        test_data_path.mkdir(parents=True, exist_ok=True)
        self._write_file_resources(file_resources=mapping_package.transformation_test_data.test_data,
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

    def _write_mapping_package(self, mapping_package: MappingPackage):
        """
            This method creates a package based on data from mapping_package.
        :param mapping_package:
        :return:
        """
        self._write_package_metadata(mapping_package=mapping_package)
        self._write_package_transform_rules(mapping_package=mapping_package)
        self._write_package_validation_rules(mapping_package=mapping_package)
        self._write_test_data_package(mapping_package=mapping_package)

    def _read_mapping_package(self, mapping_package_identifier: str) -> Optional[MappingPackage]:
        """
            This method reads a package and initializes a MappingPackage object.
        :param mapping_package_identifier:
        :return:
        """
        package_path = self.repository_path / mapping_package_identifier
        if package_path.is_dir():
            package_metadata = self._read_package_metadata(package_path)
            if (MS_MAPPING_TYPE_KEY in package_metadata and
                    package_metadata[MS_MAPPING_TYPE_KEY] == MappingPackageType.ELECTRONIC_FORMS):
                package_metadata[MS_METADATA_CONSTRAINTS_KEY] = MetadataConstraints(
                    constraints=MetadataConstraintsEform(
                        **package_metadata[MS_METADATA_CONSTRAINTS_KEY][MS_CONSTRAINTS_KEY]))
            else:
                package_metadata[MS_METADATA_CONSTRAINTS_KEY] = MetadataConstraints(
                    constraints=MetadataConstraintsStandardForm(
                        **package_metadata[MS_METADATA_CONSTRAINTS_KEY][MS_CONSTRAINTS_KEY]))
            mapping_package = MappingPackage(
                metadata_constraints=package_metadata[MS_METADATA_CONSTRAINTS_KEY],
                created_at=package_metadata[MS_CREATED_AT_KEY],
                title=package_metadata[MS_TITLE_KEY],
                ontology_version=package_metadata[MS_ONTOLOGY_VERSION_KEY],
                mapping_suite_hash_digest=package_metadata[MS_HASH_DIGEST_KEY],
                mapping_type=package_metadata[
                    MS_MAPPING_TYPE_KEY] if MS_MAPPING_TYPE_KEY in package_metadata else MappingPackageType.STANDARD_FORMS,
                version=mapping_package_read_version_from_metadata(package_metadata),
                identifier=package_metadata[
                    MS_METADATA_IDENTIFIER_KEY] if MS_METADATA_IDENTIFIER_KEY in package_metadata else mapping_package_identifier,
                transformation_rule_set=self._read_transformation_rule_set(package_path),
                shacl_test_suites=self._read_shacl_test_suites(package_path),
                sparql_test_suites=self._read_sparql_test_suites(package_path),
                transformation_test_data=self._read_test_data_package(package_path)
            )
            return mapping_package
        return None

    @classmethod
    def mapping_package_notice_path_by_group_depth(cls, path: pathlib.Path, group_depth: int = 0) -> pathlib.Path:
        return pathlib.Path(*path.parts[:(-group_depth if group_depth else None)]) if path else None

    def add(self, mapping_package: MappingPackage):
        """
            This method allows you to add MappingPackage objects to the repository.
        :param mapping_package:
        :return:
        """
        self._write_mapping_package(mapping_package=mapping_package)

    def update(self, mapping_package: MappingPackage):
        """
            This method allows you to update MappingPackage objects to the repository
        :param mapping_package:
        :return:
        """
        package_path = self.repository_path / mapping_package.identifier
        if package_path.is_dir():
            self._write_mapping_package(mapping_package=mapping_package)

    def get(self, reference) -> MappingPackage:
        """
            This method allows a MappingPackage to be obtained based on an identification reference.
        :param reference:
        :return: MappingPackage
        """
        return self._read_mapping_package(mapping_package_identifier=reference)

    def list(self) -> Iterator[MappingPackage]:
        """
            This method allows all records to be retrieved from the repository.
        :return: list of MappingPackages
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


def mapping_package_read_version_from_metadata(metadata: dict) -> str:
    version_key = MS_EFORMS_METADATA_VERSION_KEY if MS_MAPPING_TYPE_KEY in metadata and metadata[
        MS_MAPPING_TYPE_KEY] == MappingPackageType.ELECTRONIC_FORMS else MS_STANDARD_METADATA_VERSION_KEY
    return metadata.get(version_key)
