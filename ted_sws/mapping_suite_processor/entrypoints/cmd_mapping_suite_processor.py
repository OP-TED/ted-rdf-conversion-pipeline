#!/usr/bin/python3

import os
from pathlib import Path

import click

from ted_sws.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner
from ted_sws.core.adapters.logger import LOG_INFO_TEXT, LOG_WARN_TEXT
from ted_sws.mapping_suite_processor.entrypoints import cmd_yarrrml2rml_converter, cmd_sparql_generator, \
    cmd_metadata_generator

DEFAULT_MAPPINGS_PATH = 'mappings'
CMD_NAME = "CMD_MAPPING_SUITE_PROCESSOR"

"""
USAGE:
# mapping_suite_processor --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Keeps the logic to be used by Mapping Suite Processor
    """

    def __init__(
            self,
            mapping_suite_id,
            mappings_path
    ):
        super().__init__(name=CMD_NAME)
        self.mapping_suite_id = mapping_suite_id
        self.mappings_path = mappings_path

        mapping_suite_path = Path(os.path.realpath(mappings_path)) / Path(mapping_suite_id)
        if not mapping_suite_path.is_dir():
            error_msg = f"No such MappingSuite[{mapping_suite_id}]"
            self.log_failed_msg(error_msg)
            raise FileNotFoundError(error_msg)

    def run_cmd(self):
        self.log("Running " + LOG_INFO_TEXT.format(f"MappingSuite[{self.mapping_suite_id}]") + " processing ... ")
        self.log(LOG_WARN_TEXT.format("#######"))

        cmd_yarrrml2rml_converter.run(
            mapping_suite_id=self.mapping_suite_id,
            opt_mappings_path=self.mappings_path
        )

        cmd_sparql_generator.run(
            mapping_suite_id=self.mapping_suite_id,
            opt_mappings_path=self.mappings_path
        )

        cmd_metadata_generator.run(
            mapping_suite_id=self.mapping_suite_id,
            opt_mappings_path=self.mappings_path
        )

        self.log(LOG_WARN_TEXT.format("#######"))


def run(mapping_suite_id, opt_mappings_path=DEFAULT_MAPPINGS_PATH):
    cmd = CmdRunner(
        mapping_suite_id=mapping_suite_id,
        mappings_path=opt_mappings_path
    )
    cmd.run()


@click.command()
@click.argument('mapping-suite-id', nargs=1, required=True)
@click.option('-m', '--opt-mappings-path', default=DEFAULT_MAPPINGS_PATH)
def main(mapping_suite_id, opt_mappings_path):
    """
    Process Mapping Suites (identified by mapping-suite-id).
    If no mapping-suite-id is provided, all mapping suites from mappings directory will be processed.
    """
    run(mapping_suite_id, opt_mappings_path)


if __name__ == '__main__':
    main()
