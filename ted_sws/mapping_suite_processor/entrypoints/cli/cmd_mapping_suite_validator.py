#!/usr/bin/python3

from pathlib import Path
import os

import click

from ted_sws.core.adapters.cmd_runner import CmdRunnerForMappingSuite as BaseCmdRunner, DEFAULT_MAPPINGS_PATH
from ted_sws.mapping_suite_processor.services.mapping_suite_validation_service import validate_mapping_suite

CMD_NAME = "CMD_MAPPING_SUITE_VALIDATOR"
MS_VALIDATOR_ERROR_EXIT_CODE = os.EX_CONFIG

"""
USAGE:
# mapping_suite_validator --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Keeps the logic to be used by Mapping Suite Validator
    """

    def __init__(
            self,
            mapping_suite_id,
            mappings_path
    ):
        super().__init__(name=CMD_NAME)
        self.mapping_suite_id = mapping_suite_id
        self.mappings_path = mappings_path

    def run_cmd(self):
        super().run_cmd()
        mapping_suite_path: Path = Path(self.mappings_path).resolve() / Path(self.mapping_suite_id)
        is_valid: bool = validate_mapping_suite(mapping_suite_path)
        result = self.run_cmd_result(Exception("Mapping Suite has an invalid structure") if not is_valid else None)
        if not result:
            self.exit_code = MS_VALIDATOR_ERROR_EXIT_CODE


def run(mapping_suite_id=None, opt_mappings_folder=DEFAULT_MAPPINGS_PATH):
    cmd = CmdRunner(
        mapping_suite_id=mapping_suite_id,
        mappings_path=opt_mappings_folder
    )
    return cmd.run()


@click.command()
@click.argument('mapping-suite-id', nargs=1, required=False)
@click.option('-m', '--opt-mappings-folder', default=DEFAULT_MAPPINGS_PATH)
def main(mapping_suite_id, opt_mappings_folder):
    """
    Validates a Mapping Suite (structure)
    """
    return run(mapping_suite_id, opt_mappings_folder)


if __name__ == '__main__':
    main()
