#!/usr/bin/python3

import os
from pathlib import Path
from typing import List

import click

from ted_sws import config
from ted_sws.core.adapters.cmd_runner import CmdRunnerForMappingSuite as BaseCmdRunner, DEFAULT_MAPPINGS_PATH, \
    DEFAULT_OUTPUT_PATH
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapper, SerializationFormat as RMLSerializationFormat, \
    TURTLE_SERIALIZATION_FORMAT
from ted_sws.notice_transformer.services.notice_transformer import transform_test_data

CMD_NAME = "CMD_MAPPING_RUNNER"

"""
USAGE:
# mapping_runner --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Keeps the logic to be used by Notice Suite Mapping Runner CMD
    """

    def __init__(
            self,
            mapping_suite_id,
            notice_id: List[str],
            serialization_format_value,
            mappings_path=DEFAULT_MAPPINGS_PATH,
            output_path=DEFAULT_OUTPUT_PATH,
            rml_mapper=None
    ):
        super().__init__(name=CMD_NAME)
        self.repository_path = Path(os.path.realpath(mappings_path))
        self.output_path = output_path
        self.mapping_suite_id = mapping_suite_id
        self.serialization_format_value = serialization_format_value
        self.rml_mapper = rml_mapper
        self.notice_id = self._init_list_input_opts(notice_id)

    def run_cmd(self):
        super().run_cmd()

        if self.mapping_suite_id:
            self.transform(self.mapping_suite_id, self.serialization_format_value)
        else:
            for suite_id in os.listdir(self.repository_path):
                self.transform(suite_id, self.serialization_format_value)

    def transform(self, mapping_suite_id, serialization_format_value):
        """
        Transforms the Test Mapping Suites (identified by mapping_suite_id)
        """

        if not self.is_mapping_suite(mapping_suite_id):
            self.log_failed_msg("Not a MappingSuite!")
            return False

        fs_mapping_suite_path = self.repository_path / Path(mapping_suite_id)
        fs_output_path = fs_mapping_suite_path / Path(self.output_path)

        error = None
        try:
            mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=self.repository_path)
            mapping_suite = mapping_suite_repository.get(reference=mapping_suite_id)

            try:
                serialization_format = RMLSerializationFormat(serialization_format_value)
            except ValueError:
                raise ValueError('No such serialization format: %s' % serialization_format_value)

            if self.rml_mapper is None:
                rml_mapper = RMLMapper(
                    rml_mapper_path=config.RML_MAPPER_PATH,
                    serialization_format=serialization_format
                )
            else:
                rml_mapper = self.rml_mapper

            transform_test_data(mapping_suite=mapping_suite, rml_mapper=rml_mapper, output_path=fs_output_path,
                                notice_ids=self.notice_id, logger=self.get_logger())
        except Exception as e:
            error = e

        msg = mapping_suite_id
        return self.run_cmd_result(error, msg, msg)


def run(mapping_suite_id=None, notice_id=None, serialization_format=TURTLE_SERIALIZATION_FORMAT.value,
        opt_mapping_suite_id=None,
        opt_serialization_format=None, opt_mappings_folder=DEFAULT_MAPPINGS_PATH, opt_output_folder=DEFAULT_OUTPUT_PATH,
        rml_mapper=None):
    if opt_mapping_suite_id:
        mapping_suite_id = opt_mapping_suite_id
    if opt_serialization_format:
        serialization_format = opt_serialization_format
    mappings_path = opt_mappings_folder
    output_path = opt_output_folder

    cmd = CmdRunner(
        mapping_suite_id=mapping_suite_id,
        notice_id=list(notice_id or []),
        serialization_format_value=serialization_format,
        mappings_path=mappings_path,
        output_path=output_path,
        rml_mapper=rml_mapper
    )
    cmd.run()


@click.command()
@click.argument('mapping-suite-id', nargs=1, required=False)
@click.option('--notice-id', required=False, multiple=True, default=None)
@click.argument('serialization-format', nargs=1, required=False, default=TURTLE_SERIALIZATION_FORMAT.value)
@click.option('--opt-mapping-suite-id', default=None,
              help='MappingSuite ID to be processed (leave empty to process all Mapping Suites).')
@click.option('--opt-serialization-format',
              help='Serialization format (turtle (default), nquads, trig, trix, jsonld, hdt).')
@click.option('--opt-mappings-folder', default=DEFAULT_MAPPINGS_PATH)
@click.option('--opt-output-folder', default=DEFAULT_OUTPUT_PATH)
def main(mapping_suite_id, notice_id, serialization_format, opt_mapping_suite_id, opt_serialization_format,
         opt_mappings_folder,
         opt_output_folder):
    """
    Transforms the Test Mapping Suites (identified by mapping-suite-id).
    If no mapping-suite-id is provided, all mapping suites from mappings directory will be processed.
    """
    run(mapping_suite_id, notice_id, serialization_format, opt_mapping_suite_id, opt_serialization_format,
        opt_mappings_folder,
        opt_output_folder)


if __name__ == '__main__':
    main()
