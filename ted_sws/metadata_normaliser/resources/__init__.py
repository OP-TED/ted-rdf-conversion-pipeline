import pathlib

import json

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

import ted_sws.metadata_normaliser.resources.mapping_files


def get_mapping_file(mapping_file_name: str) -> dict:
    """
        get a predefined index mapping by reference to file name
    """
    with pkg_resources.path(mapping_files, mapping_file_name) as path:
        return json.loads(path.read_bytes())


RESOURCES_PATH = pathlib.Path(__file__).parent.resolve()

QUERIES_PATH = RESOURCES_PATH / 'queries'
MAPPING_FILES_PATH = RESOURCES_PATH / 'mapping_files'
