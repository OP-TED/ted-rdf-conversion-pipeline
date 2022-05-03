import pathlib

import json

import pandas as pd

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

import ted_sws.resources.mapping_files


def get_mapping_json_file(mapping_file_name: str) -> dict:
    """
        get a predefined index mapping by reference to file name
    """
    with pkg_resources.path(mapping_files, mapping_file_name) as path:
        return json.loads(path.read_bytes())


def get_mapping_csv_file(mapping_file_name: str) -> pd.DataFrame:
    """
        get content of a csv file in pandas dataframe format
    """
    with pkg_resources.path(mapping_files, mapping_file_name) as path:
        return pd.read_csv(path).fillna("")


RESOURCES_PATH = pathlib.Path(__file__).parent.resolve()

PREFIXES_PATH = RESOURCES_PATH / 'prefixes'
QUERIES_PATH = RESOURCES_PATH / 'queries'
MAPPING_FILES_PATH = RESOURCES_PATH / 'mapping_files'
XSLT_FILES_PATH = RESOURCES_PATH / 'xslt_files'
