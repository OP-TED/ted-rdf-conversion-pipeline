#!/usr/bin/python3

import os
from pathlib import Path

import click

from ted_sws.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner, DEFAULT_MAPPINGS_PATH
from ted_sws.data_manager.adapters.mapping_suite_repository import METADATA_FILE_NAME
from ted_sws.event_manager.adapters.log import LOG_INFO_TEXT
from ted_sws.mapping_suite_processor.entrypoints.cli import CONCEPTUAL_MAPPINGS_FILE_TEMPLATE
from ted_sws.mapping_suite_processor.services.conceptual_mapping_generate_metadata import \
    mapping_suite_processor_generate_metadata as generate_metadata

DEFAULT_OUTPUT_METADATA_FILE = '{mappings_path}/{mapping_suite_id}/{output_file_name}'
DEFAULT_OUTPUT_METADATA_FILE_NAME = METADATA_FILE_NAME
CMD_NAME = "CMD_METADATA_GENERATOR"

"""
USAGE:
# metadata_generator --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Keeps the logic to be used by Metadata Generator
    """

    def __init__(
            self,
            conceptual_mappings_file,
            output_metadata_file
    ):
        super().__init__(name=CMD_NAME)
        self.conceptual_mappings_file_path = Path(os.path.realpath(conceptual_mappings_file))
        self.output_metadata_file_path = Path(os.path.realpath(output_metadata_file))

        if not self.conceptual_mappings_file_path.is_file():
            error_msg = f"No such file :: [{conceptual_mappings_file}]"
            self.log_failed_msg(error_msg)
            raise FileNotFoundError(error_msg)

    def run_cmd(self):
        self.generate(self.conceptual_mappings_file_path, self.output_metadata_file_path)

    def generate(self, conceptual_mappings_file_path, output_metadata_file_path):
        """
        Generates Metadata from Conceptual Mappings
        """
        self.log("Running " + LOG_INFO_TEXT.format("Metadata") + " generation ... ")

        error = None
        try:
            generate_metadata(conceptual_mappings_file_path, output_metadata_file_path)
        except Exception as e:
            error = e

        return self.run_cmd_result(error)


def run(mapping_suite_id=None, opt_conceptual_mappings_file=None, opt_output_metadata_file=None,
        opt_mappings_folder=DEFAULT_MAPPINGS_PATH):
    if opt_conceptual_mappings_file:
        conceptual_mappings_file = opt_conceptual_mappings_file
    else:
        conceptual_mappings_file = CONCEPTUAL_MAPPINGS_FILE_TEMPLATE.format(
            mappings_path=opt_mappings_folder,
            mapping_suite_id=mapping_suite_id
        )

    if opt_output_metadata_file:
        output_metadata_file = opt_output_metadata_file
    else:
        output_metadata_file = DEFAULT_OUTPUT_METADATA_FILE.format(
            mappings_path=opt_mappings_folder,
            mapping_suite_id=mapping_suite_id,
            output_file_name=DEFAULT_OUTPUT_METADATA_FILE_NAME
        )

    cmd = CmdRunner(
        conceptual_mappings_file=conceptual_mappings_file,
        output_metadata_file=output_metadata_file
    )
    cmd.run()


@click.command()
@click.argument('mapping-suite-id', nargs=1, required=False)
@click.option('-i', '--opt-conceptual-mappings-file', help="Use to overwrite default INPUT")
@click.option('-o', '--opt-output-metadata-file', help="Use to overwrite default OUTPUT")
@click.option('-m', '--opt-mappings-folder', default=DEFAULT_MAPPINGS_PATH)
def main(mapping_suite_id, opt_conceptual_mappings_file, opt_output_metadata_file, opt_mappings_folder):
    """
    Generates Metadata from Conceptual Mappings.
    """
    run(mapping_suite_id, opt_conceptual_mappings_file, opt_output_metadata_file, opt_mappings_folder)


if __name__ == '__main__':
    main()
