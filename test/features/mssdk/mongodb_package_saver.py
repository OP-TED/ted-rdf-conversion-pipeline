#!/usr/bin/env python3
"""
Load mapping packages from ZIP archives and save to MongoDB.

Runs all test scenarios automatically:
- Loading and saving packages from ZIP files
- Converting packages (v2→v3, v3→v3L) and saving to MongoDB
"""
import argparse
import logging
import os
import shutil
import subprocess
import sys
import zipfile
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
        
        # Check if temp_folder itself is the package
        if (temp_folder / "metadata.jsonld").exists() or (temp_folder / "metadata.json").exists():
            package_root = temp_folder
        else:
            # Search for package root in nested folders (handle single and double nesting)
            # Try common nested patterns
            possible_roots = [
                temp_folder / temp_folder.name,
                temp_folder / temp_folder.name / temp_folder.name,
            ]
            
            # Also search all subdirectories for metadata files
            for item in temp_folder.iterdir():
                if item.is_dir():
                    possible_roots.append(item)
                    # Check for double nesting
                    for subitem in item.iterdir():
                        if subitem.is_dir():
                            possible_roots.append(subitem)
            
            # Find the first directory that contains metadata
            for possible_root in possible_roots:
                if possible_root.exists() and possible_root.is_dir():
                    if (possible_root / "metadata.jsonld").exists() or (possible_root / "metadata.json").exists():
                        package_root = possible_root
                        break
        
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


def run_mssdk_convert(
    from_version: str,
    to_version: str,
    package_path: Path
) -> None:
    """
    Run mssdk convert command to convert a package.
    
    Args:
        from_version: Source package version ('v2' or 'v3').
        to_version: Target package version ('v3' or 'v3L').
        package_path: Path to the package folder to convert.
        
    Raises:
        subprocess.CalledProcessError: If the convert command fails.
    """
    if not package_path.exists():
        raise FileNotFoundError(f"Package path does not exist: {package_path}")
    
    if not package_path.is_dir():
        raise NotADirectoryError(f"Package path is not a directory: {package_path}")
    
    # Build the mssdk convert command
    # Note: We use the venv's mssdk command directly
    venv_bin = project_root / ".venv" / "bin"
    mssdk_cmd = venv_bin / "mssdk"
    
    if not mssdk_cmd.exists():
        # Fallback: try to find mssdk in PATH
        mssdk_cmd = "mssdk"
    
    cmd = [
        str(mssdk_cmd),
        "convert",
        "--to-version", to_version,
        "--from-version", from_version,
        "from-package",
        str(package_path)
    ]
    
    logger.info(f"Running conversion: {' '.join(cmd)}")
    
    result = subprocess.run(
        cmd,
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=True
    )
    
    if result.stdout:
        logger.debug(f"Conversion output: {result.stdout}")
    if result.stderr:
        logger.debug(f"Conversion stderr: {result.stderr}")
    
    logger.info(f"Successfully converted package from {from_version} to {to_version}")


def create_zip_from_folder(folder_path: Path, zip_path: Path) -> None:
    """
    Create a ZIP file from a folder.
    
    Args:
        folder_path: Path to the folder to zip.
        zip_path: Path where the ZIP file should be created.
    """
    logger.info(f"Creating ZIP file from folder: {folder_path} -> {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = Path(root) / file
                # Create archive name relative to folder_path
                arcname = file_path.relative_to(folder_path)
                zipf.write(file_path, arcname)
    
    logger.info(f"Successfully created ZIP file: {zip_path}")


def find_or_create_converted_package_zip(
    original_package_path: Path,
    target_version: str
) -> Path:
    """
    Find the converted package ZIP file, or create it from the converted folder.
    
    The mssdk convert command converts the package in place or creates a new folder.
    If it's a folder, we create a ZIP from it.
    
    Args:
        original_package_path: Path to the original package folder.
        target_version: Target version ('v3' or 'v3L').
        
    Returns:
        Path to the converted package ZIP file.
        
    Raises:
        FileNotFoundError: If the converted package (ZIP or folder) cannot be found.
    """
    package_name = original_package_path.name
    package_dir = original_package_path.parent
    zip_path = package_dir / f"{package_name}.zip"
    
    # First, check if the original folder was converted in place
    # The convert command modifies the folder in place
    if original_package_path.exists() and original_package_path.is_dir():
        # Check if it's actually a package folder (has metadata)
        # For v3L, it should have metadata.jsonld; for v3, it should have metadata.jsonld
        has_metadata = (original_package_path / "metadata.jsonld").exists() or (original_package_path / "metadata.json").exists()
        if has_metadata:
            logger.info(f"Found converted package folder (in place): {original_package_path}")
            # Create ZIP from the converted folder (overwrite existing ZIP if any)
            create_zip_from_folder(original_package_path, zip_path)
            return zip_path
    
    # Check if there's a folder with the same name in the parent directory
    converted_folder = package_dir / package_name
    if converted_folder.exists() and converted_folder.is_dir():
        # Check if it's actually a package folder (has metadata)
        if (converted_folder / "metadata.jsonld").exists() or (converted_folder / "metadata.json").exists():
            logger.info(f"Found converted package folder: {converted_folder}")
            # Create ZIP from the folder
            create_zip_from_folder(converted_folder, zip_path)
            return zip_path
    
    # Also check if there's a folder with a different name (e.g., with version suffix)
    for item in package_dir.iterdir():
        if item.is_dir() and package_name in item.name:
            # Check if it's a package folder
            if (item / "metadata.jsonld").exists() or (item / "metadata.json").exists():
                logger.info(f"Found converted package folder: {item}")
                # Create ZIP from the folder
                create_zip_from_folder(item, zip_path)
                return zip_path
    
    raise FileNotFoundError(
        f"Could not find converted package (ZIP or folder) for {original_package_path}. "
        f"Expected ZIP: {zip_path} or folder: {original_package_path}"
    )


def convert_and_save_package(
    package_path: Path,
    from_version: str,
    to_version: str,
    mongodb_uri: str,
    database_name: str,
    collection_name: str
) -> PackageType:
    """
    Convert a package and save the converted package to MongoDB.
    
    Args:
        package_path: Path to the package folder to convert.
        from_version: Source package version ('v2' or 'v3').
        to_version: Target package version ('v3' or 'v3L').
        mongodb_uri: MongoDB connection URI.
        database_name: MongoDB database name.
        collection_name: MongoDB collection name.
        
    Returns:
        Saved package instance.
    """
    # Run conversion
    run_mssdk_convert(
        from_version=from_version,
        to_version=to_version,
        package_path=package_path
    )
    
    # Find or create the converted package ZIP
    converted_zip = find_or_create_converted_package_zip(package_path, to_version)
    
    # Load and save the converted package
    saved_package = load_and_save_package(
        package_path=converted_zip,
        mongodb_uri=mongodb_uri,
        database_name=database_name,
        collection_name=collection_name,
        package_version=to_version
    )
    
    return saved_package


def run_test_scenario(
    description: str,
    package_path: Path,
    package_version: Optional[str],
    mongodb_uri: str,
    database_name: str,
    collection_name: str,
    is_conversion: bool = False,
    from_version: Optional[str] = None,
    to_version: Optional[str] = None
) -> None:
    """
    Run a single test scenario.
    
    Args:
        description: Human-readable description of the test scenario.
        package_path: Path to package archive file or folder.
        package_version: Package version ('v1', 'v2', 'v3', 'v3L').
        mongodb_uri: MongoDB connection URI.
        database_name: MongoDB database name.
        collection_name: MongoDB collection name.
        is_conversion: If True, this is a conversion scenario.
        from_version: Source version for conversion (if is_conversion is True).
        to_version: Target version for conversion (if is_conversion is True).
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"Test Scenario: {description}")
    logger.info(f"Path: {package_path}")
    if is_conversion:
        logger.info(f"Conversion: {from_version} → {to_version}")
    else:
        logger.info(f"Version: {package_version}")
    logger.info(f"MongoDB: {database_name}.{collection_name}")
    logger.info(f"{'='*80}")
    
    if not package_path.exists():
        logger.warning(f"  SKIPPED: Path does not exist: {package_path}")
        return
    
    try:
        if is_conversion:
            saved_package = convert_and_save_package(
                package_path=package_path,
                from_version=from_version,
                to_version=to_version,
                mongodb_uri=mongodb_uri,
                database_name=database_name,
                collection_name=collection_name
            )
            logger.info(
                f"  ✓ Successfully converted and saved package: {saved_package.id} "
                f"({from_version} → {to_version}) to MongoDB ({database_name}.{collection_name})"
            )
        else:
            saved_package = load_and_save_package(
                package_path=package_path,
                mongodb_uri=mongodb_uri,
                database_name=database_name,
                collection_name=collection_name,
                package_version=package_version
            )
            logger.info(
                f"  ✓ Successfully loaded and saved package: {saved_package.id} "
                f"to MongoDB ({database_name}.{collection_name})"
            )
    except Exception as error:
        logger.error(f"  ✗ FAILED: {type(error).__name__}: {error}")


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
    
    If no arguments are provided, runs all test scenarios automatically.
    Otherwise, runs with the provided arguments.
    
    Raises:
        All exceptions propagate and cause script to fail.
    """
    args = parse_arguments()
    
    mongodb_uri = args.mongodb_uri or get_mongodb_uri()
    database_name = args.database or get_database_name()
    collection_name = args.collection or get_collection_name()
    
    # If no package path provided, run all test scenarios
    if args.package_path is None:
        # Base path for test data
        test_data_root = project_root / "test" / "test_data" / "mssdk"
        
        # Define all test scenarios
        test_scenarios = [
            # Conversion scenarios
            {
                "description": "Convert v2 → v3 and save to MongoDB",
                "package_path": test_data_root / "mapping_package_v2" / "package_eforms_29_v1.9_changed",
                "package_version": None,
                "is_conversion": True,
                "from_version": "v2",
                "to_version": "v3"
            },
            {
                "description": "Convert v3 → v3L and save to MongoDB",
                "package_path": test_data_root / "mapping_package_v3" / "package_eforms_sdk1.13_epo4.0_changed",
                "package_version": None,
                "is_conversion": True,
                "from_version": "v3",
                "to_version": "v3L"
            },
        ]
        
        logger.info("="*80)
        logger.info("Starting Package Conversion and Save Test Suite")
        logger.info(f"MongoDB URI: {mongodb_uri}")
        logger.info(f"Database: {database_name}")
        logger.info(f"Collection: {collection_name}")
        logger.info("="*80)
        
        # Run all test scenarios
        for scenario in test_scenarios:
            run_test_scenario(
                description=scenario["description"],
                package_path=scenario["package_path"],
                package_version=scenario["package_version"],
                mongodb_uri=mongodb_uri,
                database_name=database_name,
                collection_name=collection_name,
                is_conversion=scenario["is_conversion"],
                from_version=scenario.get("from_version"),
                to_version=scenario.get("to_version")
            )
        
        logger.info("\n" + "="*80)
        logger.info("Test Suite Completed")
        logger.info("="*80)
    else:
        # Run with provided arguments
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
