#!/usr/bin/env python3
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional, Union, Tuple, Type

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, DocumentTooLarge, OperationFailure

# MSSDK imports - package loaders
from mapping_suite_sdk.mapping_package_v1.adapters.mp_v1_loader import MappingPackageV1Loader
from mapping_suite_sdk.mapping_package_v2.adapters.mp_v2_loader import MappingPackageV2Loader
from mapping_suite_sdk.mapping_package_v3.adapters.mp_v3_package_loader import MappingPackageV3Loader
from mapping_suite_sdk.mapping_package_v3.adapters.mp_v3L_package_loader import MappingPackageV3LightweightLoader

# MSSDK imports - package savers
from mapping_suite_sdk.mapping_package_v1.adapters.mp_v1_package_saver import MappingPackageV1Saver
from mapping_suite_sdk.mapping_package_v2.adapters.mp_v2_package_saver import MappingPackageV2Saver
from mapping_suite_sdk.mapping_package_v3.adapters.mp_v3_package_saver import MappingPackageV3Saver
from mapping_suite_sdk.mapping_package_v3.adapters.mp_v3L_package_saver import MappingPackageV3LightweightSaver

# MSSDK imports - models
from mapping_suite_sdk.mapping_package_v1.models import MappingPackageV1
from mapping_suite_sdk.mapping_package_v2.models import MappingPackageV2
from mapping_suite_sdk.mapping_package_v3.models import MappingPackageV3, MappingPackageV3Lightweight

# MSSDK imports - services
from mapping_suite_sdk.mapping_package_v1.services.load_mapping_package_v1 import (
    load_mapping_package_v1_from_mongo_db
)
from mapping_suite_sdk.mapping_package_v2.services.load_mapping_package_v2 import (
    load_mapping_package_v2_from_mongo_db
)
from mapping_suite_sdk.mapping_package_v3.services.load_mapping_package_v3 import (
    load_mapping_package_v2_from_mongo_db as load_mapping_package_v3_from_mongo_db
)
from mapping_suite_sdk.mapping_package_v3.services.load_mapping_package_v3_lightweight import (
    load_mapping_package_v2_from_mongo_db as load_mapping_package_v3L_from_mongo_db
)

# MSSDK imports - core
from mapping_suite_sdk.core.adapters.repository import MongoDBRepository
from mapping_suite_sdk.core.adapters.extractor import ArchiveExtractor

# Configuration constants
DEFAULT_MONGODB_URI = "mongodb://127.0.0.1:27017/"
DEFAULT_DATABASE_NAME = "mapping_package_test"
DEFAULT_COLLECTION_NAME = "mapping_package"
MONGODB_CONNECTION_TIMEOUT_MS = 5000


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enable debug logging for MSSDK
logging.getLogger('mapping_suite_sdk').setLevel(logging.DEBUG)

# Type aliases
PackageType = Union[MappingPackageV1, MappingPackageV2, MappingPackageV3, MappingPackageV3Lightweight]
SaverType = Union[
    MappingPackageV1Saver,
    MappingPackageV2Saver,
    MappingPackageV3Saver,
    MappingPackageV3LightweightSaver
]


def validate_package_file_exists(package_path: Path) -> None:
    """
    Validate that the package archive file exists.
    
    Args:
        package_path: Path to the package archive file.
        
    Raises:
        FileNotFoundError: If the package file does not exist.
    """
    if not package_path.exists():
        raise FileNotFoundError(f"Package file not found: {package_path}")
    logger.info(f"Package file validated: {package_path}")


def get_mongodb_uri() -> str:
    """
    Get MongoDB URI from environment variable or default to local.
    
    Returns:
        MongoDB connection URI string.
    """
    mongodb_uri = os.getenv('MONGODB_URI')
    if mongodb_uri:
        return mongodb_uri
    
    logger.info(f"Using default local MongoDB connection: {DEFAULT_MONGODB_URI}")
    return DEFAULT_MONGODB_URI


def create_mongodb_client(mongodb_uri: Optional[str] = None) -> MongoClient:
    """
    Create and verify MongoDB client connection.
    
    Args:
        mongodb_uri: Optional MongoDB connection URI. If None, uses default or env var.
        
    Returns:
        Connected MongoClient instance.
        
    Raises:
        ValueError: If authentication fails or connection cannot be established.
    """
    if mongodb_uri is None:
        mongodb_uri = get_mongodb_uri()
    
    mongo_client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=MONGODB_CONNECTION_TIMEOUT_MS)
    
    try:
        mongo_client.admin.command('ping')
        logger.info("Connected to MongoDB")
        return mongo_client
    except OperationFailure as error:
        if "Authentication failed" in str(error):
            error_msg = (
                f"MongoDB authentication failed for URI: {mongodb_uri}. "
                f"If using local MongoDB without authentication, use: {DEFAULT_MONGODB_URI}"
            )
            raise ValueError(error_msg) from error
        raise ValueError(f"Failed to connect to MongoDB: {error}") from error


def load_package_from_archive(
    archive_path: Path,
    package_version: Optional[str] = None
) -> Tuple[PackageType, str]:
    """
    Load a mapping package from archive by trying version loaders.
    
    Args:
        archive_path: Path to package archive file.
        package_version: Optional package version ('v1', 'v2', 'v3', 'v3L'). If None, tries all.
        
    Returns:
        Tuple of (loaded package, detected version name).
        
    Raises:
        ValueError: If package cannot be loaded with any version.
    """
    extractor = ArchiveExtractor()
    
    with extractor.extract_temporary(archive_path) as temp_folder:
        # Resolve package root (handle nested folder structure)
        package_root = temp_folder
        nested_root = temp_folder / temp_folder.name
        if nested_root.exists() and nested_root.is_dir():
            if (nested_root / "metadata.jsonld").exists():
                package_root = nested_root
            elif (nested_root / "metadata.json").exists():
                package_root = nested_root
        
        # Define loaders in priority order
        loaders = [
            (MappingPackageV3Loader(), "v3"),
            (MappingPackageV3LightweightLoader(), "v3L"),
            (MappingPackageV2Loader(), "v2"),
            (MappingPackageV1Loader(), "v1"),
        ]
        
        # Filter to specific version if provided
        if package_version:
            loaders = [(loader, v) for loader, v in loaders if v == package_version]
            if not loaders:
                raise ValueError(f"Invalid package version: {package_version}. Must be one of: v1, v2, v3, v3L")
        
        # Try each loader until one succeeds
        last_error = None
        for loader, version_name in loaders:
            try:
                loaded_package = loader.load(package_root)
                logger.info(f"Package loaded successfully as {version_name}")
                return loaded_package, version_name
            except Exception as error:
                last_error = error
                logger.debug(f"{version_name} loader failed: {type(error).__name__}: {error}")
        
        # All loaders failed
        if last_error:
            raise ValueError(f"Failed to load package with any version. Last error: {last_error}") from last_error
        raise ValueError("Failed to load package: no loaders attempted")


def _save_package_with_saver(
    saver: SaverType,
    package: PackageType,
    mongo_client: MongoClient,
    database_name: str,
    collection_name: str,
    version_name: str
) -> PackageType:
    """
    Save package to MongoDB using a specific saver.
    
    Args:
        saver: Package saver instance to use.
        package: Loaded package instance to save.
        mongo_client: MongoDB client instance.
        database_name: MongoDB database name.
        collection_name: MongoDB collection name.
        version_name: Human-readable version name for logging.
        
    Returns:
        Saved package instance if successful.
        
    Raises:
        Exception: Any exception from the saver is propagated.
    """
    logger.debug(f"Attempting to save as {version_name}...")
    
    # Delete existing document if it exists (to avoid duplicate key error)
    collection = mongo_client[database_name][collection_name]
    existing_doc = collection.find_one({"_id": package.id})
    if existing_doc:
        collection.delete_one({"_id": package.id})
        logger.info(f"Deleted existing package with ID: {package.id}")
    
    saved_package = saver.save(
        mapping_package=package,
        mongo_client=mongo_client,
        database_name=database_name,
        collection_name=collection_name
    )
    logger.info(f"Package saved successfully as {version_name} with ID: {saved_package.id}")
    return saved_package


def save_package_to_mongodb(
    package: PackageType,
    mongo_client: MongoClient,
    database_name: str,
    collection_name: str,
    version_name: str
) -> PackageType:
    """
    Save loaded package to MongoDB using appropriate saver.
    
    Args:
        package: Loaded package instance to save.
        mongo_client: MongoDB client instance.
        database_name: MongoDB database name.
        collection_name: MongoDB collection name.
        version_name: Package version name ('v1', 'v2', 'v3', 'v3L').
        
    Returns:
        Saved package instance.
        
    Raises:
        ValueError: If package type is unsupported.
        Exception: Any exception from the saver is propagated.
    """
    # Select appropriate saver based on package type
    if isinstance(package, MappingPackageV3Lightweight):
        saver = MappingPackageV3LightweightSaver()
    elif isinstance(package, MappingPackageV3):
        saver = MappingPackageV3Saver()
    elif isinstance(package, MappingPackageV2):
        saver = MappingPackageV2Saver()
    elif isinstance(package, MappingPackageV1):
        saver = MappingPackageV1Saver()
    else:
        raise ValueError(f"Unsupported package type: {type(package)}")
    
    return _save_package_with_saver(
        saver=saver,
        package=package,
        mongo_client=mongo_client,
        database_name=database_name,
        collection_name=collection_name,
        version_name=version_name
    )


def _create_repository_for_package(
    package: PackageType,
    mongo_client: MongoClient,
    database_name: str,
    collection_name: str
) -> MongoDBRepository:
    """
    Create appropriate MongoDB repository based on package type.
    
    Args:
        package: Package instance to determine repository type.
        mongo_client: MongoDB client instance.
        database_name: MongoDB database name.
        collection_name: MongoDB collection name.
        
    Returns:
        MongoDBRepository instance configured for the package type.
    """
    if isinstance(package, MappingPackageV3Lightweight):
        return MongoDBRepository[MappingPackageV3Lightweight](
            model_class=MappingPackageV3Lightweight,
            mongo_client=mongo_client,
            database_name=database_name,
            collection_name=collection_name
        )
    elif isinstance(package, MappingPackageV3):
        return MongoDBRepository[MappingPackageV3](
            model_class=MappingPackageV3,
            mongo_client=mongo_client,
            database_name=database_name,
            collection_name=collection_name
        )
    elif isinstance(package, MappingPackageV2):
        return MongoDBRepository[MappingPackageV2](
            model_class=MappingPackageV2,
            mongo_client=mongo_client,
            database_name=database_name,
            collection_name=collection_name
        )
    else:  # V1
        return MongoDBRepository[MappingPackageV1](
            model_class=MappingPackageV1,
            mongo_client=mongo_client,
            database_name=database_name,
            collection_name=collection_name
        )


def _load_package_by_type(
    package_id: str,
    package: PackageType,
    repository: MongoDBRepository
) -> PackageType:
    """
    Load package from MongoDB using appropriate loader function.
    
    Args:
        package_id: Package identifier.
        package: Package instance to determine loader type.
        repository: MongoDB repository instance.
        
    Returns:
        Loaded package instance.
    """
    if isinstance(package, MappingPackageV3Lightweight):
        return load_mapping_package_v3L_from_mongo_db(package_id, repository)
    elif isinstance(package, MappingPackageV3):
        return load_mapping_package_v3_from_mongo_db(package_id, repository)
    elif isinstance(package, MappingPackageV2):
        return load_mapping_package_v2_from_mongo_db(package_id, repository)
    else:  # V1
        return load_mapping_package_v1_from_mongo_db(package_id, repository)


def load_package_from_mongodb(
    package_id: str,
    saved_package: PackageType,
    mongo_client: MongoClient,
    database_name: str,
    collection_name: str
) -> PackageType:
    """
    Load package from MongoDB by ID using appropriate loader.
    
    Args:
        package_id: Package identifier.
        saved_package: Previously saved package instance (used to determine type).
        mongo_client: MongoDB client instance.
        database_name: MongoDB database name.
        collection_name: MongoDB collection name.
        
    Returns:
        Loaded package instance.
        
    Raises:
        ValueError: If package cannot be loaded or ID mismatch occurs.
    """
    repository = _create_repository_for_package(saved_package, mongo_client, database_name, collection_name)
    loaded_package = _load_package_by_type(package_id, saved_package, repository)
    
    if loaded_package is None:
        raise ValueError(f"Package with ID {package_id} not found in MongoDB after saving.")
    
    logger.info(f"Package loaded successfully with ID: {loaded_package.id}")
    return loaded_package


def verify_package_integrity(saved_package: PackageType, loaded_package: PackageType) -> None:
    """
    Verify that loaded package matches saved package.
    
    Args:
        saved_package: Originally saved package instance.
        loaded_package: Package loaded from MongoDB.
        
    Raises:
        ValueError: If package IDs do not match.
    """
    if loaded_package.id != saved_package.id:
        raise ValueError(f"Package ID mismatch: {loaded_package.id} != {saved_package.id}")
    logger.info("Package integrity verification passed")


def load_and_save_package(
    package_path: Path,
    mongodb_uri: str,
    database_name: str,
    collection_name: str,
    package_version: Optional[str] = None
) -> PackageType:
    """
    Orchestrate the complete flow: validate, load from archive, save, load from MongoDB, and verify.
    
    Args:
        package_path: Path to package archive file.
        mongodb_uri: MongoDB connection URI.
        database_name: MongoDB database name.
        collection_name: MongoDB collection name.
        package_version: Optional package version ('v1', 'v2', 'v3', 'v3L').
        
    Returns:
        Saved package instance.
    """
    validate_package_file_exists(package_path)
    
    # Load package from archive
    loaded_package, detected_version = load_package_from_archive(
        archive_path=package_path,
        package_version=package_version
    )
    
    # Save package to MongoDB
    save_mongo_client = create_mongodb_client(mongodb_uri)
    try:
        saved_package = save_package_to_mongodb(
            package=loaded_package,
            mongo_client=save_mongo_client,
            database_name=database_name,
            collection_name=collection_name,
            version_name=detected_version
        )
    finally:
        save_mongo_client.close()
    
    # Create a fresh client for loading (in case save closed the original)
    load_mongo_client = create_mongodb_client(mongodb_uri)
    try:
        loaded_from_mongo = load_package_from_mongodb(
            package_id=saved_package.id,
            saved_package=saved_package,
            mongo_client=load_mongo_client,
            database_name=database_name,
            collection_name=collection_name
        )
        verify_package_integrity(saved_package, loaded_from_mongo)
    finally:
        load_mongo_client.close()
    
    return saved_package


def get_database_name() -> str:
    """Get database name from environment variable or default."""
    return os.getenv('MONGODB_DATABASE', DEFAULT_DATABASE_NAME)


def get_collection_name() -> str:
    """Get collection name from environment variable or default."""
    return os.getenv('MONGODB_COLLECTION', DEFAULT_COLLECTION_NAME)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Load mapping package using MSSDK and save to MongoDB"
    )
    parser.add_argument(
        'package_path',
        type=Path,
        nargs='?',
        help='Path to package archive file (ZIP)'
    )
    parser.add_argument(
        '--mongodb-uri',
        type=str,
        default=None,
        help=f'MongoDB connection URI (overrides MONGODB_URI env var, default: {DEFAULT_MONGODB_URI})'
    )
    parser.add_argument(
        '--database',
        type=str,
        default=None,
        help=f'Database name (default: {DEFAULT_DATABASE_NAME} or MONGODB_DATABASE env var)'
    )
    parser.add_argument(
        '--collection',
        type=str,
        default=None,
        help=f'Collection name (default: {DEFAULT_COLLECTION_NAME} or MONGODB_COLLECTION env var)'
    )
    parser.add_argument(
        '--version',
        type=str,
        default=None,
        choices=['v1', 'v2', 'v3', 'v3L'],
        help='Package version to use (v1, v2, v3, v3L). If not specified, tries all versions sequentially.'
    )
    return parser.parse_args()


def main() -> None:
    """
    Main entry point for the script.
    
    Raises:
        All exceptions propagate and cause script to fail.
    """
    args = parse_arguments()
    
    if args.package_path is None:
        raise ValueError("Package path is required. Provide as argument.")
    
    mongodb_uri = args.mongodb_uri or get_mongodb_uri()
    database_name = args.database or get_database_name()
    collection_name = args.collection or get_collection_name()
    
    saved_package = load_and_save_package(
        package_path=args.package_path,
        mongodb_uri=mongodb_uri,
        database_name=database_name,
        collection_name=collection_name,
        package_version=args.version
    )
    logger.info(
        f"Test completed successfully. Package ID: {saved_package.id}, "
        f"Database: {database_name}, Collection: {collection_name}"
    )


if __name__ == "__main__":
    main()
