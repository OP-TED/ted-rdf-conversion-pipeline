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

DEFAULT_MAPPINGS_PATH = 'mappings'

"""
SETUP:
1) Clone ted-sws repository on the same directory level as ted-sws-artefacts project.
2) Go to ted-sws directory.
3) Run the following commands (it will install the requirements and set the path to rplmapper.jar):
   # make install && make local-dotenv-file 
   (.env file must already be created)
4) Go to ted-sws-artefacts directory.
5) Create a symlink in ted-sws-artefacts project's root directory:
   # ln -sf ../ted-sws/ted_sws/notice_transformer/entrypoints/cmd_mapping_suite_transformer.py transformer
6) Usage:
   # ./transformer --help
"""


class CmdRunner:
    """
    Keeps the logic to be used by Notice Suite Transformer CMD
    """

    def __init__(self, mappings_path, output_path):
        self.fs_repository_path = Path(os.path.realpath(mappings_path))
        self.output_path = output_path

    def is_mapping_suite(self, suite_id):
        suite_path = self.fs_repository_path / Path(suite_id)
        return os.path.isdir(suite_path) and any(f == METADATA_FILE_NAME for f in os.listdir(suite_path))

    def transform(self, mapping_suite_id):
        """
        Transforms the Test Mapping Suites (identified by mapping_suite_id)
        """
        click.echo(
            "Running process for " + "\033[1;93m{}\033[00m".format("MappingSuite[" + mapping_suite_id + "]") + " ... ",
            nl=False
        )
        if not self.is_mapping_suite(mapping_suite_id):
            click.echo("\033[1;91m{}\033[00m".format("FAILED"))
            click.echo("\033[1;91m {}\033[00m".format('FAILED') + " :: " + "Not a MappingSuite!")
            return False

        fs_mapping_suite_path = self.fs_repository_path / Path(mapping_suite_id)
        fs_output_path = fs_mapping_suite_path / Path(self.output_path)

        error = None
        try:
            mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=self.fs_repository_path)
            mapping_suite = mapping_suite_repository.get(reference=mapping_suite_id)
            notice_transformer.transform_test_data(mapping_suite=mapping_suite,
                                                   rml_mapper=RMLMapper(rml_mapper_path=config.RML_MAPPER_PATH),
                                                   output_path=fs_output_path)
        except Exception as e:
            error = e

        suite_text = ":: " + mapping_suite_id
        if error:
            click.echo("\033[1;91m{}\033[00m".format("FAILED"))
            click.echo("\033[0;91m {}\033[00m".format(type(error).__name__ + ' :: ' + str(error)))
            click.echo("\033[1;91m {}\033[00m".format('FAILED') + '  ' + suite_text)
            return False
        else:
            click.echo("\033[1;92m{}\033[00m".format("DONE"))
            click.echo("\033[1;92m {}\033[00m".format('SUCCESS') + '  ' + suite_text)
            return True


@click.command()
@click.argument('mapping-suite-id', nargs=1, required=False)
@click.option('--opt-mapping-suite-id', default=None,
              help='MappingSuite ID to be processed (leave empty to process all Mapping Suites).')
@click.option('--opt-mappings-path', default=DEFAULT_MAPPINGS_PATH)
@click.option('--opt-output-path', default='output')
def transform_notice(mapping_suite_id, opt_mapping_suite_id, opt_mappings_path, opt_output_path) -> click.BaseCommand:
    """
    Transforms the Test Mapping Suites (identified by mapping-suite-id).
    If no mapping-suite-id is provided, all mapping suites from mappings directory will be processed.
    """
    if not mapping_suite_id:
        mapping_suite_id = opt_mapping_suite_id
    mappings_path = opt_mappings_path
    output_path = opt_output_path

    cmd = CmdRunner(mappings_path=mappings_path, output_path=output_path)
    if mapping_suite_id:
        cmd.transform(mapping_suite_id)
    else:
        for suite_id in os.listdir(cmd.fs_repository_path):
            cmd.transform(suite_id)


if __name__ == '__main__':
    transform_notice()
