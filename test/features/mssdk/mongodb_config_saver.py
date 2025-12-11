#!/usr/bin/env python3
"""
Integration test script for MongoDB save/load functionality.

This script tests saving and loading a MappingSuite and config to/from MongoDB.

Usage:
    python test/features/mssdk/mongodb_config_saver.py [suite_path] [config_path]
    
Environment variables:
    MONGODB_URI: MongoDB connection URI (optional, falls back to default)
    MONGODB_DATABASE: Database name (default: mapping_suite_test)
    MONGODB_COLLECTION: Collection name (default: mapping_suites)
    MONGODB_CONFIG_COLLECTION: Config collection name (default: mapping_suite_configs)
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

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
    
    Raises:
        All exceptions propagate and cause script to fail.
    """
    args = parse_arguments()
    
    # Determine suite_path and config_path from arguments
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
    
    mongodb_uri = args.mongodb_uri or get_mongodb_uri()
    database_name = args.database or get_database_name()
    suite_collection_name = args.suite_collection or get_suite_collection_name()
    config_collection_name = args.config_collection or get_config_collection_name()
    
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
