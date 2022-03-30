#!/usr/bin/python3

import os
import sys

module_path = os.path.dirname(os.path.realpath(__file__)) + '/../../../'
sys.path.append(module_path)

import click
from pathlib import Path

from ted_sws import config
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem, \
    METADATA_FILE_NAME
from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapper
import ted_sws.notice_transformer.services.notice_transformer as notice_transformer

REPOSITORY_PATH = 'mappings'

"""
Create a symlink in ted-sws-artefacts project's root directory
(ted-sws project must be on the same dir level as ted-sws-artefacts project):
ln -sf ../ted-sws/ted_sws/notice_transformer/entrypoints/cmd_suite_transformer.py transformer.py

Run for help:
./transformer --help
"""


class CmdRunner:
    """
    Keeps the logic to be used by Notice Suite Transformer CMD
    """

    def __init__(self, output_path):
        self.fs_repository_path = Path(os.path.realpath(REPOSITORY_PATH))
        self.output_path = output_path

    def transform(self, mapping_suite_id):
        """
        Transforms the Test Mapping Suites (identified by mapping_suite_id)
        """
        fs_mapping_suite_path = self.fs_repository_path / Path(mapping_suite_id)
        fs_output_path = fs_mapping_suite_path / Path(self.output_path)

        mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=self.fs_repository_path)
        mapping_suite = mapping_suite_repository.get(reference=mapping_suite_id)
        notice_transformer.transform_test_data(mapping_suite=mapping_suite,
                                               rml_mapper=RMLMapper(rml_mapper_path=config.RML_MAPPER_PATH),
                                               output_path=fs_output_path)


@click.command()
@click.option('--mapping-suite-id', default=None, help='Mapping Suite ID.')
def transform_notice(mapping_suite_id, output_path='output'):
    """
    Transforms the Test Mapping Suites (identified by mapping-suite-id).
    If no mapping-suite-id is provided, all mapping suites from mappings dir will be transformed.
    """

    cmd = CmdRunner(output_path=output_path)
    if mapping_suite_id:
        cmd.transform(mapping_suite_id)
    else:
        for suite_id in os.listdir(cmd.fs_repository_path):
            if any(f == METADATA_FILE_NAME for f in os.listdir(cmd.fs_repository_path / Path(suite_id))):
                cmd.transform(suite_id)
                print("PARSED :: Suite :: " + suite_id)


if __name__ == '__main__':
    transform_notice()
