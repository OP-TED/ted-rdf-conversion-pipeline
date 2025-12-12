#!/usr/bin/env python3
"""
Integration test script for MongoDB save/load functionality.

This script tests saving and loading a MappingSuite and config to/from MongoDB.
Also includes package conversion tests (v2→v3→v3L).

Runs all test scenarios automatically when called without arguments.
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Optional, Tuple, Union

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from pymongo import MongoClient
from pymongo.errors import OperationFailure

from mapping_suite_sdk.core.adapters.repository import MongoDBRepository
from mapping_suite_sdk.mapping_suite.models import MappingSuite
from mapping_suite_sdk.mapping_suite.services.load_mapping_suite import (
    load_mapping_suite_from_folder,
    load_mapping_suite_from_mongo_db
)
from mapping_suite_sdk.mapping_suite.services.save_mapping_suite import save_mapping_suite_to_mongo_db

# Package-related imports for conversion tests
from mapping_suite_sdk.mapping_package_v1.adapters.mp_v1_loader import MappingPackageV1Loader
from mapping_suite_sdk.mapping_package_v2.adapters.mp_v2_loader import MappingPackageV2Loader
from mapping_suite_sdk.mapping_package_v3.adapters.mp_v3_package_loader import MappingPackageV3Loader
from mapping_suite_sdk.mapping_package_v3.adapters.mp_v3L_package_loader import MappingPackageV3LightweightLoader
from mapping_suite_sdk.mapping_package_v1.adapters.mp_v1_package_saver import MappingPackageV1Saver
from mapping_suite_sdk.mapping_package_v2.adapters.mp_v2_package_saver import MappingPackageV2Saver
from mapping_suite_sdk.mapping_package_v3.adapters.mp_v3_package_saver import MappingPackageV3Saver
from mapping_suite_sdk.mapping_package_v3.adapters.mp_v3L_package_saver import MappingPackageV3LightweightSaver
from mapping_suite_sdk.mapping_package_v1.models import MappingPackageV1
from mapping_suite_sdk.mapping_package_v2.models import MappingPackageV2
from mapping_suite_sdk.mapping_package_v3.models import MappingPackageV3, MappingPackageV3Lightweight
from mapping_suite_sdk.core.adapters.extractor import ArchiveExtractor

# Package type alias
PackageType = Union[MappingPackageV1, MappingPackageV2, MappingPackageV3, MappingPackageV3Lightweight]

# Configuration constants
DEFAULT_MONGODB_URI = "mongodb://127.0.0.1:27017/"
DEFAULT_DATABASE_NAME = "mapping_suite_test"
DEFAULT_COLLECTION_NAME = "mapping_suites"
DEFAULT_CONFIG_COLLECTION_NAME = "mapping_suite_configs"
MONGODB_CONNECTION_TIMEOUT_MS = 5000

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_path_exists(path: Path, path_type: str) -> None:
    """
    Validate that the specified path exists.
    
    Args:
        path: Path to validate.
        path_type: Type of path for error message (e.g., "suite", "config").
        
    Raises:
        FileNotFoundError: If the path does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"{path_type.capitalize()} path does not exist: {path}")
    logger.info(f"{path_type.capitalize()} path validated: {path}")


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


def load_mapping_suite(suite_path: Path) -> MappingSuite:
    """
    Load mapping suite from filesystem.
    
    Args:
        suite_path: Path to mapping suite folder.
        
    Returns:
        Loaded MappingSuite instance.
    """
    validate_path_exists(suite_path, "suite")
    suite = load_mapping_suite_from_folder(suite_path)
    logger.info(f"Loaded mapping suite: {suite.id}")
    logger.info(f"  Description: {suite.mapping_suite_config.mapping_suite_metadata.mapping_suite_description}")
    return suite


def load_config(config_path: Path) -> dict:
    """
    Load config JSON file.
    
    Args:
        config_path: Path to config JSON file.
        
    Returns:
        Config dictionary.
    """
    validate_path_exists(config_path, "config")
    with config_path.open('r', encoding='utf-8') as f:
        config = json.load(f)
    logger.info(f"Loaded config from: {config_path}")
    return config


def save_config_to_mongodb(
    config: dict,
    config_id: str,
    mongo_client: MongoClient,
    database_name: str,
    collection_name: str
) -> None:
    """
    Save config to MongoDB.
    
    Args:
        config: Config dictionary to save.
        config_id: Unique identifier for the config document.
        mongo_client: MongoDB client instance.
        database_name: MongoDB database name.
        collection_name: MongoDB collection name.
    """
    collection = mongo_client[database_name][collection_name]
    
    # Delete existing config if it exists
    existing = collection.find_one({"_id": config_id})
    if existing:
        collection.delete_one({"_id": config_id})
        logger.info(f"Deleted existing config with ID: {config_id}")
    
    # Save config with _id
    config_doc = {"_id": config_id, **config}
    collection.insert_one(config_doc)
    logger.info(f"Saved config to MongoDB with ID: {config_id}")


def load_config_from_mongodb(
    config_id: str,
    mongo_client: MongoClient,
    database_name: str,
    collection_name: str
) -> dict:
    """
    Load config from MongoDB.
    
    Args:
        config_id: Config document identifier.
        mongo_client: MongoDB client instance.
        database_name: MongoDB database name.
        collection_name: MongoDB collection name.
        
    Returns:
        Config dictionary.
        
    Raises:
        ValueError: If config not found.
    """
    collection = mongo_client[database_name][collection_name]
    config_doc = collection.find_one({"_id": config_id})
    
    if config_doc is None:
        raise ValueError(f"Config with ID {config_id} not found in MongoDB")
    
    # Remove _id from returned config
    config = {k: v for k, v in config_doc.items() if k != "_id"}
    logger.info(f"Loaded config from MongoDB with ID: {config_id}")
    return config


def save_suite_to_mongodb(
    suite: MappingSuite,
    mongo_client: MongoClient,
    database_name: str,
    collection_name: str
) -> MappingSuite:
    """
    Save mapping suite to MongoDB.
    
    Args:
        suite: MappingSuite instance to save.
        mongo_client: MongoDB client instance.
        database_name: MongoDB database name.
        collection_name: MongoDB collection name.
        
    Returns:
        Saved MappingSuite instance.
    """
    repository = MongoDBRepository(
        model_class=MappingSuite,
        mongo_client=mongo_client,
        database_name=database_name,
        collection_name=collection_name
    )
    
    # Delete existing suite if it exists
    existing = repository.collection.find_one({"_id": suite.id})
    if existing:
        repository.collection.delete_one({"_id": suite.id})
        logger.info(f"Deleted existing suite with ID: {suite.id}")
    
    saved_suite = save_mapping_suite_to_mongo_db(suite, repository)
    logger.info(f"Saved mapping suite to MongoDB with ID: {saved_suite.id}")
    return saved_suite


def load_suite_from_mongodb(
    suite_id: str,
    mongo_client: MongoClient,
    database_name: str,
    collection_name: str
) -> MappingSuite:
    """
    Load mapping suite from MongoDB.
    
    Args:
        suite_id: Suite identifier.
        mongo_client: MongoDB client instance.
        database_name: MongoDB database name.
        collection_name: MongoDB collection name.
        
    Returns:
        Loaded MappingSuite instance.
    """
    repository = MongoDBRepository(
        model_class=MappingSuite,
        mongo_client=mongo_client,
        database_name=database_name,
        collection_name=collection_name
    )
    
    suite = load_mapping_suite_from_mongo_db(suite_id, repository)
    if suite is None:
        raise ValueError(f"Suite with ID {suite_id} not found in MongoDB")
    
    logger.info(f"Loaded mapping suite from MongoDB with ID: {suite.id}")
    return suite


def verify_suite_integrity(original_suite: MappingSuite, loaded_suite: MappingSuite) -> None:
    """
    Verify that loaded suite matches original suite.
    
    Args:
        original_suite: Originally saved suite instance.
        loaded_suite: Suite loaded from MongoDB.
        
    Raises:
        ValueError: If suites do not match.
    """
    if loaded_suite.id != original_suite.id:
        raise ValueError(f"Suite ID mismatch: {loaded_suite.id} != {original_suite.id}")
    
    original_desc = original_suite.mapping_suite_config.mapping_suite_metadata.mapping_suite_description
    loaded_desc = loaded_suite.mapping_suite_config.mapping_suite_metadata.mapping_suite_description
    
    if loaded_desc != original_desc:
        raise ValueError(f"Suite description mismatch: {loaded_desc} != {original_desc}")
    
    logger.info("Suite integrity verification passed")


def verify_config_integrity(original_config: dict, loaded_config: dict) -> None:
    """
    Verify that loaded config matches original config.
    
    Args:
        original_config: Originally saved config dictionary.
        loaded_config: Config loaded from MongoDB.
        
    Raises:
        ValueError: If configs do not match.
    """
    if original_config != loaded_config:
        raise ValueError("Config mismatch: loaded config does not match original")
    logger.info("Config integrity verification passed")


def save_and_load_suite_and_config(
    suite_path: Optional[Path],
    config_path: Optional[Path],
    mongodb_uri: str,
    database_name: str,
    suite_collection_name: str,
    config_collection_name: str
) -> None:
    """
    Orchestrate saving and loading suite and config to/from MongoDB.
    
    Args:
        suite_path: Optional path to mapping suite folder.
        config_path: Optional path to config JSON file.
        mongodb_uri: MongoDB connection URI.
        database_name: MongoDB database name.
        suite_collection_name: MongoDB collection name for suites.
        config_collection_name: MongoDB collection name for configs.
    """
    if not suite_path and not config_path:
        raise ValueError("At least one of suite_path or config_path must be provided")
    
    # Handle suite if provided
    saved_suite = None
    if suite_path:
        # Save suite to MongoDB
        save_mongo_client = create_mongodb_client(mongodb_uri)
        try:
            suite = load_mapping_suite(suite_path)
            saved_suite = save_suite_to_mongodb(
                suite=suite,
                mongo_client=save_mongo_client,
                database_name=database_name,
                collection_name=suite_collection_name
            )
        finally:
            save_mongo_client.close()
        
        # Create fresh client for loading (in case save closed the original)
        load_mongo_client = create_mongodb_client(mongodb_uri)
        try:
            # Load suite from MongoDB and verify
            loaded_suite = load_suite_from_mongodb(
                suite_id=saved_suite.id,
                mongo_client=load_mongo_client,
                database_name=database_name,
                collection_name=suite_collection_name
            )
            verify_suite_integrity(saved_suite, loaded_suite)
        finally:
            load_mongo_client.close()
    
    # Handle config if provided
    if config_path:
        mongo_client = create_mongodb_client(mongodb_uri)
        try:
            config = load_config(config_path)
            config_id = config.get("mapping_suite_config", {}).get(
                "mapping_suite_metadata", {}
            ).get("mapping_suite_identifier", "default")
            
            # Save config to MongoDB
            save_config_to_mongodb(
                config=config,
                config_id=config_id,
                mongo_client=mongo_client,
                database_name=database_name,
                collection_name=config_collection_name
            )
            
            # Load config from MongoDB and verify
            loaded_config = load_config_from_mongodb(
                config_id=config_id,
                mongo_client=mongo_client,
                database_name=database_name,
                collection_name=config_collection_name
            )
            verify_config_integrity(config, loaded_config)
        finally:
            mongo_client.close()
    
    logger.info(f"Test completed successfully. Database: {database_name}")
    if saved_suite:
        logger.info(f"Suite ID: {saved_suite.id}, Suite Collection: {suite_collection_name}")
    if config_path:
        logger.info(f"Config Collection: {config_collection_name}")


def get_database_name() -> str:
    """Get database name from environment variable or default."""
    return os.getenv('MONGODB_DATABASE', DEFAULT_DATABASE_NAME)


def get_suite_collection_name() -> str:
    """Get suite collection name from environment variable or default."""
    return os.getenv('MONGODB_COLLECTION', DEFAULT_COLLECTION_NAME)


def get_config_collection_name() -> str:
    """Get config collection name from environment variable or default."""
    return os.getenv('MONGODB_CONFIG_COLLECTION', DEFAULT_CONFIG_COLLECTION_NAME)


# Package conversion constants (reusing from mongodb_package_saver.py)
DEFAULT_PACKAGE_DATABASE_NAME = "mapping_package_test"
DEFAULT_PACKAGE_COLLECTION_NAME = "mapping_package"


def run_mssdk_convert(
    from_version: str,
    to_version: str,
    package_path: Path
) -> None:
    """Run mssdk convert command to convert a package."""
    if not package_path.exists():
        raise FileNotFoundError(f"Package path does not exist: {package_path}")
    
    if not package_path.is_dir():
        raise NotADirectoryError(f"Package path is not a directory: {package_path}")
    
    venv_bin = project_root / ".venv" / "bin"
    mssdk_cmd = venv_bin / "mssdk"
    
    if not mssdk_cmd.exists():
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
    """Create a ZIP file from a folder."""
    logger.info(f"Creating ZIP file from folder: {folder_path} -> {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(folder_path)
                zipf.write(file_path, arcname)
    
    logger.info(f"Successfully created ZIP file: {zip_path}")


def find_or_create_converted_package_zip(
    original_package_path: Path,
    target_version: str
) -> Path:
    """Find the converted package ZIP file, or create it from the converted folder."""
    package_name = original_package_path.name
    package_dir = original_package_path.parent
    zip_path = package_dir / f"{package_name}.zip"
    
    # Check if the original folder was converted in place
    if original_package_path.exists() and original_package_path.is_dir():
        has_metadata = (original_package_path / "metadata.jsonld").exists() or (original_package_path / "metadata.json").exists()
        if has_metadata:
            logger.info(f"Found converted package folder (in place): {original_package_path}")
            create_zip_from_folder(original_package_path, zip_path)
            return zip_path
    
    # Check if ZIP already exists
    if zip_path.exists():
        logger.info(f"Found converted package ZIP: {zip_path}")
        return zip_path
    
    raise FileNotFoundError(
        f"Could not find converted package (ZIP or folder) for {original_package_path}. "
        f"Expected ZIP: {zip_path} or folder: {original_package_path}"
    )


def load_package_from_archive(
    archive_path: Path,
    package_version: Optional[str] = None
) -> Tuple[PackageType, str]:
    """Load a mapping package from archive by trying version loaders."""
    extractor = ArchiveExtractor()
    
    with extractor.extract_temporary(archive_path) as temp_folder:
        package_root = temp_folder
        
        # Check for nested folder structure
        if (temp_folder / "metadata.jsonld").exists() or (temp_folder / "metadata.json").exists():
            package_root = temp_folder
        else:
            possible_roots = [
                temp_folder / temp_folder.name,
                temp_folder / temp_folder.name / temp_folder.name,
            ]
            for item in temp_folder.iterdir():
                if item.is_dir():
                    possible_roots.append(item)
                    for subitem in item.iterdir():
                        if subitem.is_dir():
                            possible_roots.append(subitem)
            
            for possible_root in possible_roots:
                if possible_root.exists() and possible_root.is_dir():
                    if (possible_root / "metadata.jsonld").exists() or (possible_root / "metadata.json").exists():
                        package_root = possible_root
                        break
        
        loaders = [
            (MappingPackageV3Loader(), "v3"),
            (MappingPackageV3LightweightLoader(), "v3L"),
            (MappingPackageV2Loader(), "v2"),
            (MappingPackageV1Loader(), "v1"),
        ]
        
        if package_version:
            loaders = [(loader, v) for loader, v in loaders if v == package_version]
            if not loaders:
                raise ValueError(f"Invalid package version: {package_version}. Must be one of: v1, v2, v3, v3L")
        
        last_error = None
        for loader, version_name in loaders:
            try:
                loaded_package = loader.load(package_root)
                logger.info(f"Package loaded successfully as {version_name}")
                return loaded_package, version_name
            except Exception as error:
                last_error = error
                logger.debug(f"{version_name} loader failed: {type(error).__name__}: {error}")
        
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
    """Save loaded package to MongoDB using appropriate saver."""
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


def convert_v2_to_v3_to_v3l_and_save(
    package_path: Path,
    mongodb_uri: str,
    database_name: str,
    collection_name: str
) -> PackageType:
    """
    Convert v2 → v3 → v3L and save the final package to MongoDB.
    
    Args:
        package_path: Path to the v2 package folder.
        mongodb_uri: MongoDB connection URI.
        database_name: MongoDB database name.
        collection_name: MongoDB collection name.
        
    Returns:
        Saved package instance.
    """
    # Step 1: Convert v2 → v3
    logger.info("Step 1: Converting v2 → v3")
    run_mssdk_convert(
        from_version="v2",
        to_version="v3",
        package_path=package_path
    )
    
    # Step 2: Convert v3 → v3L (on the same folder, now v3)
    logger.info("Step 2: Converting v3 → v3L")
    run_mssdk_convert(
        from_version="v3",
        to_version="v3L",
        package_path=package_path
    )
    
    # Step 3: Find or create ZIP from converted folder
    logger.info("Step 3: Creating ZIP from converted folder")
    converted_zip = find_or_create_converted_package_zip(package_path, "v3L")
    
    # Step 4: Load and save to MongoDB
    logger.info("Step 4: Loading and saving to MongoDB")
    loaded_package, detected_version = load_package_from_archive(converted_zip, "v3L")
    
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


def run_conversion_test_scenario(
    description: str,
    package_path: Path,
    mongodb_uri: str,
    database_name: str,
    collection_name: str
) -> None:
    """Run a conversion test scenario."""
    logger.info(f"\n{'='*80}")
    logger.info(f"Test Scenario: {description}")
    logger.info(f"Path: {package_path}")
    logger.info(f"MongoDB: {database_name}.{collection_name}")
    logger.info(f"{'='*80}")
    
    if not package_path.exists():
        logger.warning(f"  SKIPPED: Path does not exist: {package_path}")
        return
    
    try:
        saved_package = convert_v2_to_v3_to_v3l_and_save(
            package_path=package_path,
            mongodb_uri=mongodb_uri,
            database_name=database_name,
            collection_name=collection_name
        )
        logger.info(
            f"  ✓ Successfully converted (v2 → v3 → v3L) and saved package: {saved_package.id} "
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
        description="Load mapping suite and config using MSSDK and save to MongoDB"
    )
    parser.add_argument(
        'path',
        type=Path,
        nargs='?',
        help='Path to mapping suite folder or config JSON file'
    )
    parser.add_argument(
        '--suite',
        type=Path,
        default=None,
        help='Path to mapping suite folder (if path is a config file)'
    )
    parser.add_argument(
        '--config',
        type=Path,
        default=None,
        help='Path to mapping suite config JSON file (if path is a suite folder)'
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
        '--suite-collection',
        type=str,
        default=None,
        help=f'Suite collection name (default: {DEFAULT_COLLECTION_NAME} or MONGODB_COLLECTION env var)'
    )
    parser.add_argument(
        '--config-collection',
        type=str,
        default=None,
        help=f'Config collection name (default: {DEFAULT_CONFIG_COLLECTION_NAME} or MONGODB_CONFIG_COLLECTION env var)'
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
    suite_collection_name = args.suite_collection or get_suite_collection_name()
    config_collection_name = args.config_collection or get_config_collection_name()
    
    # If no path provided, run all test scenarios
    if args.path is None and args.suite is None and args.config is None:
        # Base path for test data
        test_data_root = project_root / "test" / "test_data" / "mssdk"
        
        # Package conversion test scenario
        package_database_name = os.getenv('MONGODB_PACKAGE_DATABASE', DEFAULT_PACKAGE_DATABASE_NAME)
        package_collection_name = os.getenv('MONGODB_PACKAGE_COLLECTION', DEFAULT_PACKAGE_COLLECTION_NAME)
        
        logger.info("="*80)
        logger.info("Starting MongoDB Config and Package Conversion Test Suite")
        logger.info(f"MongoDB URI: {mongodb_uri}")
        logger.info("="*80)
        
        # Conversion test: v2 → v3 → v3L
        conversion_test_scenario = {
            "description": "Convert v2 → v3 → v3L and save to MongoDB",
            "package_path": test_data_root / "mapping_package_v2_2" / "package_eforms_29_v1.9_changed",
        }
        
        run_conversion_test_scenario(
            description=conversion_test_scenario["description"],
            package_path=conversion_test_scenario["package_path"],
            mongodb_uri=mongodb_uri,
            database_name=package_database_name,
            collection_name=package_collection_name
        )
        
        logger.info("\n" + "="*80)
        logger.info("Test Suite Completed")
        logger.info("="*80)
    else:
        # Run with provided arguments
        suite_path = None
        config_path = None
        
        if args.path:
            # Check if path is a file (config) or directory (suite)
            if args.path.is_file():
                config_path = args.path
                suite_path = args.suite
            elif args.path.is_dir():
                suite_path = args.path
                config_path = args.config
            else:
                raise ValueError(f"Path does not exist: {args.path}")
        else:
            # Use explicit flags if provided
            suite_path = args.suite
            config_path = args.config
        
        if not suite_path and not config_path:
            raise ValueError("At least one of suite path or config path must be provided")
        
        save_and_load_suite_and_config(
            suite_path=suite_path,
            config_path=config_path,
            mongodb_uri=mongodb_uri,
            database_name=database_name,
            suite_collection_name=suite_collection_name,
            config_collection_name=config_collection_name
        )


if __name__ == "__main__":
    main()
