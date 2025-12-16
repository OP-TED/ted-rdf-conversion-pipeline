#!/usr/bin/env python3
"""
Load mapping packages from unzipped folders and save to MongoDB.
- Single and batch loading/saving for v2, v3, v3L packages
"""
import logging
import os
import sys
from pathlib import Path
from typing import Optional, Union, Tuple, List

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pymongo import MongoClient
from pymongo.errors import OperationFailure

# Use MSSDK services directly
from mapping_suite_sdk.mapping_package_v1.services.load_mapping_package_v1 import (
    load_mapping_package_v1_from_folder
)
from mapping_suite_sdk.mapping_package_v2.services.load_mapping_package_v2 import (
    load_mapping_package_v2_from_folder
)
from mapping_suite_sdk.mapping_package_v3.services.load_mapping_package_v3 import (
    load_mapping_package_v3_from_folder
)
from mapping_suite_sdk.mapping_package_v3.services.load_mapping_package_v3_lightweight import (
    load_mapping_package_v3_lightweight_from_folder
)
from mapping_suite_sdk.mapping_package_v1.services.save_mapping_package_v1 import (
    save_mapping_package_v1_to_mongo_db
)
from mapping_suite_sdk.mapping_package_v2.services.save_mapping_package_v2 import (
    save_mapping_package_v2_to_mongo_db
)
from mapping_suite_sdk.mapping_package_v3.services.save_mapping_package_v3 import (
    save_mapping_package_v3_to_mongo_db
)
from mapping_suite_sdk.mapping_package_v3.services.save_mapping_package_v3_lightweight import (
    save_mapping_package_v3_lightweight_to_mongo_db
)
from mapping_suite_sdk.mapping_package_v1.models import MappingPackageV1
from mapping_suite_sdk.mapping_package_v2.models import MappingPackageV2
from mapping_suite_sdk.mapping_package_v3.models import MappingPackageV3, MappingPackageV3Lightweight

# Type aliases
from typing import Union
PackageType = Union[MappingPackageV1, MappingPackageV2, MappingPackageV3, MappingPackageV3Lightweight]

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

def is_package_folder(folder_path: Path) -> bool:
    """Check if a folder contains a mapping package (has metadata.json or metadata.jsonld)."""
    return (folder_path / "metadata.json").exists() or (folder_path / "metadata.jsonld").exists()


def find_package_folders(root_path: Path) -> List[Path]:
    """Find all package folders in a directory."""
    if not root_path.exists():
        raise FileNotFoundError(f"Directory does not exist: {root_path}")
    
    if not root_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root_path}")
    
    package_folders = []
    
    # Check if root itself is a package
    if is_package_folder(root_path):
        package_folders.append(root_path)
        logger.info(f"Found package folder: {root_path}")
        return package_folders
    
    # Search subdirectories
    for item in root_path.iterdir():
        if item.is_dir() and is_package_folder(item):
            package_folders.append(item)
            logger.info(f"Found package folder: {item}")
    
    return package_folders


def load_package_from_folder(
    folder_path: Path,
    package_version: Optional[str] = None
) -> Tuple[PackageType, str]:
    """
    Load a mapping package from a folder using MSSDK services.
    
    Args:
        folder_path: Path to package folder.
        package_version: Optional package version ('v1', 'v2', 'v3', 'v3L'). If None, tries all.
        
    Returns:
        Tuple of (loaded package, detected version name).
    """
    if not folder_path.exists():
        raise FileNotFoundError(f"Package folder does not exist: {folder_path}")
    
    if not folder_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {folder_path}")
    
    if not is_package_folder(folder_path):
        raise ValueError(f"Folder does not appear to be a package folder (no metadata.json/jsonld): {folder_path}")
    
    # Define loaders in priority order (newest first)
    loaders = [
        (load_mapping_package_v3_from_folder, "v3"),
        (load_mapping_package_v3_lightweight_from_folder, "v3L"),
        (load_mapping_package_v2_from_folder, "v2"),
        (load_mapping_package_v1_from_folder, "v1"),
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
            loaded_package = loader(folder_path)
            logger.info(f"Package loaded successfully as {version_name} from: {folder_path}")
            return loaded_package, version_name
        except Exception as error:
            last_error = error
            logger.debug(f"{version_name} loader failed: {type(error).__name__}: {error}")
    
    # All loaders failed
    if last_error:
        raise ValueError(f"Failed to load package with any version. Last error: {last_error}") from last_error
    raise ValueError("Failed to load package: no loaders attempted")


def save_package_to_mongodb(
    package: PackageType,
    mongo_client: MongoClient,
    database_name: str,
    collection_name: str,
    version_name: str
) -> PackageType:
    """
    Save loaded package to MongoDB using MSSDK services.
    
    Args:
        package: Loaded package instance to save.
        mongo_client: MongoDB client instance.
        database_name: MongoDB database name.
        collection_name: MongoDB collection name.
        version_name: Package version name ('v1', 'v2', 'v3', 'v3L').
        
    Returns:
        Saved package instance.
    """
    # Delete existing document if it exists (to avoid duplicate key error)
    collection = mongo_client[database_name][collection_name]
    existing_doc = collection.find_one({"_id": package.id})
    if existing_doc:
        collection.delete_one({"_id": package.id})
        logger.info(f"Deleted existing package with ID: {package.id}")
    
    # Select appropriate service based on package type
    if isinstance(package, MappingPackageV3Lightweight):
        saved_package = save_mapping_package_v3_lightweight_to_mongo_db(
            mapping_package=package,
            mongo_client=mongo_client,
            database_name=database_name,
            collection_name=collection_name
        )
    elif isinstance(package, MappingPackageV3):
        saved_package = save_mapping_package_v3_to_mongo_db(
            mapping_package=package,
            mongo_client=mongo_client,
            database_name=database_name,
            collection_name=collection_name
        )
    elif isinstance(package, MappingPackageV2):
        saved_package = save_mapping_package_v2_to_mongo_db(
            mapping_package=package,
            mongo_client=mongo_client,
            database_name=database_name,
            collection_name=collection_name
        )
    elif isinstance(package, MappingPackageV1):
        saved_package = save_mapping_package_v1_to_mongo_db(
            mapping_package=package,
            mongo_client=mongo_client,
            database_name=database_name,
            collection_name=collection_name
        )
    else:
        raise ValueError(f"Unsupported package type: {type(package)}")
    
    logger.info(f"Package saved successfully as {version_name} with ID: {saved_package.id}")
    return saved_package


def get_mongodb_uri() -> str:
    """Get MongoDB URI from environment variable or default to local."""
    mongodb_uri = os.getenv('MONGODB_URI')
    if mongodb_uri:
        return mongodb_uri
    logger.info(f"Using default local MongoDB connection: {DEFAULT_MONGODB_URI}")
    return DEFAULT_MONGODB_URI


def create_mongodb_client(mongodb_uri: Optional[str] = None) -> MongoClient:
    """Create and verify MongoDB client connection."""
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


# save_package_to_mongodb is imported from our adapter


def load_and_save_single_package(
    folder_path: Path,
    mongodb_uri: str,
    database_name: str,
    collection_name: str,
    package_version: Optional[str] = None
) -> PackageType:
    """
    Load a single package from folder and save to MongoDB.
    
    Args:
        folder_path: Path to package folder.
        mongodb_uri: MongoDB connection URI.
        database_name: MongoDB database name.
        collection_name: MongoDB collection name.
        package_version: Optional package version ('v1', 'v2', 'v3', 'v3L').
        
    Returns:
        Saved package instance.
    """
    # Load package from folder
    loaded_package, detected_version = load_package_from_folder(folder_path, package_version)
    
    # Save to MongoDB
    mongo_client = create_mongodb_client(mongodb_uri)
    try:
        saved_package = save_package_to_mongodb(
            package=loaded_package,
            mongo_client=mongo_client,
            database_name=database_name,
            collection_name=collection_name,
            version_name=detected_version
        )
        return saved_package
    finally:
        mongo_client.close()


def load_and_save_all_packages(
    root_path: Path,
    mongodb_uri: str,
    database_name: str,
    collection_name: str,
    package_version: Optional[str] = None
) -> List[Tuple[PackageType, Path]]:
    """
    Load all packages from folder and save to MongoDB.
    
    Args:
        root_path: Root directory containing package folders.
        mongodb_uri: MongoDB connection URI.
        database_name: MongoDB database name.
        collection_name: MongoDB collection name.
        package_version: Optional package version ('v1', 'v2', 'v3', 'v3L').
        
    Returns:
        List of tuples: (saved package, folder path).
    """
    package_folders = find_package_folders(root_path)
    
    if not package_folders:
        raise ValueError(f"No package folders found in: {root_path}")
    
    mongo_client = create_mongodb_client(mongodb_uri)
    saved_packages = []
    errors = []
    
    try:
        for folder_path in package_folders:
            try:
                # Load package from folder
                loaded_package, detected_version = load_package_from_folder(folder_path, package_version)
                
                # Save to MongoDB (using MSSDK services)
                saved_package = save_package_to_mongodb(
                    package=loaded_package,
                    mongo_client=mongo_client,
                    database_name=database_name,
                    collection_name=collection_name,
                    version_name=detected_version
                )
                
                saved_packages.append((saved_package, folder_path))
                logger.info(f"Successfully loaded and saved package {saved_package.id} from {folder_path}")
            except Exception as error:
                errors.append((folder_path, error))
                logger.error(f"Failed to load/save package from {folder_path}: {type(error).__name__}: {error}")
    finally:
        mongo_client.close()
    
    if not saved_packages and errors:
        # All packages failed - raise the first error
        folder, error = errors[0]
        raise ValueError(f"Failed to load/save any packages. First error from {folder}: {error}") from error
    
    if errors:
        logger.warning(f"Saved {len(saved_packages)} packages, {len(errors)} failed")
    
    return saved_packages


def get_database_name() -> str:
    """Get database name from environment variable or default."""
    return os.getenv('MONGODB_DATABASE', DEFAULT_DATABASE_NAME)


def get_collection_name() -> str:
    """Get collection name from environment variable or default."""
    return os.getenv('MONGODB_COLLECTION', DEFAULT_COLLECTION_NAME)


def run_test_scenario(
    description: str,
    folder_path: Path,
    package_version: Optional[str],
    load_all: bool,
    mongodb_uri: str,
    database_name: str,
    collection_name: str
) -> None:
    """
    Run a single test scenario.
    
    Args:
        description: Human-readable description of the test scenario.
        folder_path: Path to package folder or directory.
        package_version: Package version ('v1', 'v2', 'v3', 'v3L').
        load_all: If True, load all packages from folder; if False, load single package.
        mongodb_uri: MongoDB connection URI.
        database_name: MongoDB database name.
        collection_name: MongoDB collection name.
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"Test Scenario: {description}")
    logger.info(f"Path: {folder_path}")
    logger.info(f"Version: {package_version}")
    logger.info(f"Mode: {'Load and save all packages' if load_all else 'Load and save single package'}")
    logger.info(f"MongoDB: {database_name}.{collection_name}")
    logger.info(f"{'='*80}")
    
    if not folder_path.exists():
        logger.warning(f"  SKIPPED: Path does not exist: {folder_path}")
        return
    
    try:
        if load_all:
            saved_packages = load_and_save_all_packages(
                root_path=folder_path,
                mongodb_uri=mongodb_uri,
                database_name=database_name,
                collection_name=collection_name,
                package_version=package_version
            )
            logger.info(f"  ✓ Successfully loaded and saved {len(saved_packages)} packages:")
            for saved_package, pkg_folder_path in saved_packages:
                logger.info(f"    - {saved_package.id} from {pkg_folder_path}")
        else:
            saved_package = load_and_save_single_package(
                folder_path=folder_path,
                mongodb_uri=mongodb_uri,
                database_name=database_name,
                collection_name=collection_name,
                package_version=package_version
            )
            logger.info(
                f"  ✓ Successfully loaded and saved package: {saved_package.id} "
                f"from {folder_path} to MongoDB ({database_name}.{collection_name})"
            )
    except Exception as error:
        logger.error(f"  ✗ FAILED: {type(error).__name__}: {error}")


def main() -> None:
    """Main entry point - runs all test scenarios automatically."""
    # Base path for test data
    test_data_root = project_root / "test" / "test_data" / "mssdk"
    
    # MongoDB configuration
    mongodb_uri = get_mongodb_uri()
    database_name = get_database_name()
    collection_name = get_collection_name()
    
    # Define all test scenarios
    test_scenarios = [
        # V2 Tests
        {
            "description": "Load and save single v2 package",
            "folder_path": test_data_root / "mapping_package_v2" / "package_eforms_29_v1.9_changed",
            "version": "v2",
            "load_all": False
        },
        {
            "description": "Load and save all v2 packages",
            "folder_path": test_data_root / "mapping_package_v2",
            "version": "v2",
            "load_all": True
        },
        # V3 Tests
        {
            "description": "Load and save single v3 package",
            "folder_path": test_data_root / "mapping_package_v3" / "package_eforms_sdk1.13_epo4.0_changed",
            "version": "v3",
            "load_all": False
        },
        {
            "description": "Load and save all v3 packages",
            "folder_path": test_data_root / "mapping_package_v3",
            "version": "v3",
            "load_all": True
        },
        # V3L Tests
        {
            "description": "Load and save single v3L package",
            "folder_path": test_data_root / "mapping_package_v3L" / "package_eforms_sdk1.13_epo4.0_changed",
            "version": "v3L",
            "load_all": False
        },
        {
            "description": "Load and save all v3L packages",
            "folder_path": test_data_root / "mapping_package_v3L",
            "version": "v3L",
            "load_all": True
        },
    ]
    
    logger.info("="*80)
    logger.info("Starting Package Load and Save Test Suite")
    logger.info(f"MongoDB URI: {mongodb_uri}")
    logger.info(f"Database: {database_name}")
    logger.info(f"Collection: {collection_name}")
    logger.info("="*80)
    
    # Run all test scenarios
    for scenario in test_scenarios:
        run_test_scenario(
            description=scenario["description"],
            folder_path=scenario["folder_path"],
            package_version=scenario["version"],
            load_all=scenario["load_all"],
            mongodb_uri=mongodb_uri,
            database_name=database_name,
            collection_name=collection_name
        )
    
    logger.info("\n" + "="*80)
    logger.info("Test Suite Completed")
    logger.info("="*80)


if __name__ == "__main__":
    main()

