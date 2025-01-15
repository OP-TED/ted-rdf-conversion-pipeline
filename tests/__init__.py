#!/usr/bin/python3

# __init__.py
# Date:  03/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

""" """
import os
import pathlib
import shutil
import tempfile

from ted_sws import RUN_ENV_NAME, RUN_TEST_ENV_VAL

os.environ[RUN_ENV_NAME] = RUN_TEST_ENV_VAL

TESTS_PATH = pathlib.Path(__file__).parent.resolve()

TEST_DATA_PATH = TESTS_PATH / 'test_data'

AIRFLOW_DAG_FOLDER = TESTS_PATH.parent.resolve() / "dags"


class temporary_copy(object):
    """
        This class realizes the temporary context mechanism for an existing directory.
        It can be used when you want to perform operations on a copy in an existing directory.
        Once the context is closed, the temporary directory will be deleted.
    """

    def __init__(self, original_path):
        self.original_path = original_path

    def __enter__(self):
        temp_dir = tempfile.gettempdir()
        base_path = os.path.basename(self.original_path)
        self.path = pathlib.Path(os.path.join(temp_dir, base_path))
        self.path.mkdir(parents=True, exist_ok=True)
        shutil.copytree(self.original_path, self.path, dirs_exist_ok=True)
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.path)
