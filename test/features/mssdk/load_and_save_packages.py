#!/usr/bin/env python3
"""
Load mapping packages from unzipped folders and save to MongoDB.

Combines functionality from:
- package_loader.py: Loads packages from folders
- mongodb_package_saver.py: Saves packages to MongoDB

Supports:
- Loading and saving a single package from a folder
- Loading and saving all packages from a folder
"""
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional, Union, Tuple, List

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from pymongo import MongoClient
from pymongo.errors import OperationFailure

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

# Type aliases
PackageType = Union[MappingPackageV1, MappingPackageV2, MappingPackageV3, MappingPackageV3Lightweight]
SaverType = Union[
    MappingPackageV1Saver,
    MappingPackageV2Saver,
    MappingPackageV3Saver,
    MappingPackageV3LightweightSaver
]


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
    Load a mapping package from a folder by trying version loaders.
    
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
            loaded_package = loader.load(folder_path)
            logger.info(f"Package loaded successfully as {version_name} from: {folder_path}")
            return loaded_package, version_name
        except Exception as error:
            last_error = error
            logger.debug(f"{version_name} loader failed: {type(error).__name__}: {error}")
    
    # All loaders failed
    if last_error:
        raise ValueError(f"Failed to load package with any version. Last error: {last_error}") from last_error
    raise ValueError("Failed to load package: no loaders attempted")


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


def _save_package_with_saver(
    saver: SaverType,
    package: PackageType,
    mongo_client: MongoClient,
    database_name: str,
    collection_name: str,
    version_name: str
) -> PackageType:
    """Save package to MongoDB using a specific saver."""
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
                
                # Save to MongoDB
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


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Load mapping packages from folders and save to MongoDB"
    )
    parser.add_argument(
        'folder_path',
        type=Path,
        help='Path to package folder or directory containing packages'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Load and save all packages from folder (instead of single package)'
    )
    parser.add_argument(
        '--version',
        type=str,
        default=None,
        choices=['v1', 'v2', 'v3', 'v3L'],
        help='Package version to use (v1, v2, v3, v3L). If not specified, tries all versions sequentially.'
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
    return parser.parse_args()


def main() -> None:
    """Main entry point for the script."""
    args = parse_arguments()
    
    mongodb_uri = args.mongodb_uri or get_mongodb_uri()
    database_name = args.database or get_database_name()
    collection_name = args.collection or get_collection_name()
    
    if args.all:
        # Load and save all packages from folder
        saved_packages = load_and_save_all_packages(
            root_path=args.folder_path,
            mongodb_uri=mongodb_uri,
            database_name=database_name,
            collection_name=collection_name,
            package_version=args.version
        )
        logger.info(f"Successfully loaded and saved {len(saved_packages)} packages:")
        for saved_package, folder_path in saved_packages:
            logger.info(f"  - {saved_package.id} from {folder_path}")
    else:
        # Load and save single package from folder
        saved_package = load_and_save_single_package(
            folder_path=args.folder_path,
            mongodb_uri=mongodb_uri,
            database_name=database_name,
            collection_name=collection_name,
            package_version=args.version
        )
        logger.info(
            f"Successfully loaded and saved package: {saved_package.id} "
            f"from {args.folder_path} to MongoDB ({database_name}.{collection_name})"
        )


if __name__ == "__main__":
    main()

