#!/usr/bin/env python3
"""
Load mapping packages from unzipped folders using MSSDK.

Supports:
- Loading a single package from a folder
- Loading all packages from a folder (v2 or v3)
- Converting packages: v2→v3, v2→v3→v3L, v3→v3L
"""
import argparse
import logging
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Union, Tuple, List

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# MSSDK imports - package loaders
from mapping_suite_sdk.mapping_package_v1.adapters.mp_v1_loader import MappingPackageV1Loader
from mapping_suite_sdk.mapping_package_v2.adapters.mp_v2_loader import MappingPackageV2Loader
from mapping_suite_sdk.mapping_package_v3.adapters.mp_v3_package_loader import MappingPackageV3Loader
from mapping_suite_sdk.mapping_package_v3.adapters.mp_v3L_package_loader import MappingPackageV3LightweightLoader

# MSSDK imports - models
from mapping_suite_sdk.mapping_package_v1.models import MappingPackageV1
from mapping_suite_sdk.mapping_package_v2.models import MappingPackageV2
from mapping_suite_sdk.mapping_package_v3.models import MappingPackageV3, MappingPackageV3Lightweight

# Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Type aliases
PackageType = Union[MappingPackageV1, MappingPackageV2, MappingPackageV3, MappingPackageV3Lightweight]


def is_package_folder(folder_path: Path) -> bool:
    """
    Check if a folder contains a mapping package (has metadata.json or metadata.jsonld).
    
    Args:
        folder_path: Path to folder to check.
        
    Returns:
        True if folder appears to be a package folder.
    """
    return (folder_path / "metadata.json").exists() or (folder_path / "metadata.jsonld").exists()


def find_package_folders(root_path: Path) -> List[Path]:
    """
    Find all package folders in a directory.
    
    Args:
        root_path: Root directory to search.
        
    Returns:
        List of paths to package folders.
    """
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
        
    Raises:
        ValueError: If package cannot be loaded with any version.
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


def load_all_packages_from_folder(
    root_path: Path,
    package_version: Optional[str] = None
) -> List[Tuple[PackageType, str, Path]]:
    """
    Load all packages from a folder.
    
    Args:
        root_path: Root directory containing package folders.
        package_version: Optional package version ('v1', 'v2', 'v3', 'v3L'). If None, tries all.
        
    Returns:
        List of tuples: (loaded package, detected version, folder path).
    """
    package_folders = find_package_folders(root_path)
    
    if not package_folders:
        raise ValueError(f"No package folders found in: {root_path}")
    
    loaded_packages = []
    errors = []
    
    for folder_path in package_folders:
        try:
            package, version = load_package_from_folder(folder_path, package_version)
            loaded_packages.append((package, version, folder_path))
            logger.info(f"Successfully loaded package {package.id} from {folder_path}")
        except Exception as error:
            errors.append((folder_path, error))
            logger.error(f"Failed to load package from {folder_path}: {type(error).__name__}: {error}")
    
    if not loaded_packages and errors:
        # All packages failed - raise the first error
        folder, error = errors[0]
        raise ValueError(f"Failed to load any packages. First error from {folder}: {error}") from error
    
    if errors:
        logger.warning(f"Loaded {len(loaded_packages)} packages, {len(errors)} failed")
    
    return loaded_packages


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Load mapping packages from unzipped folders using MSSDK"
    )
    parser.add_argument(
        'folder_path',
        type=Path,
        help='Path to package folder or directory containing packages'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Load all packages from folder (instead of single package)'
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
    """Main entry point for the script."""
    args = parse_arguments()
    
    if args.all:
        # Load all packages from folder
        loaded_packages = load_all_packages_from_folder(
            root_path=args.folder_path,
            package_version=args.version
        )
        logger.info(f"Successfully loaded {len(loaded_packages)} packages:")
        for package, version, folder_path in loaded_packages:
            logger.info(f"  - {package.id} ({version}) from {folder_path}")
    else:
        # Load single package from folder
        package, version = load_package_from_folder(
            folder_path=args.folder_path,
            package_version=args.version
        )
        logger.info(f"Successfully loaded package: {package.id} ({version}) from {args.folder_path}")


if __name__ == "__main__":
    main()

