#!/usr/bin/python3

import os
from pathlib import Path

import click

from ted_sws.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner
from ted_sws.core.adapters.logger import LOG_INFO_TEXT
from ted_sws.mapping_suite_processor.adapters.yarrrml2rml_converter import YARRRML2RMLConverter

DEFAULT_MAPPINGS_PATH = 'mappings'
DEFAULT_YARRRML_INPUT_FILE = '{mappings_path}/{mapping_suite_id}/transformation/technical_mappings.yarrrml.yaml'
DEFAULT_RML_OUTPUT_FILE = '{mappings_path}/{mapping_suite_id}/transformation/mappings/{output_file_name}'
DEFAULT_RML_OUTPUT_FILE_NAME = 'mappings.rml.ttl'
CMD_NAME = "CMD_YARRRML2RML_CONVERTER"

"""
USAGE:
# yarrrml2rml_converter --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Keeps the logic to be used by YARRRML to RML Convertor
    """

    def __init__(
            self,
            yarrrml_input_file,
            rml_output_file
    ):
        super().__init__(name=CMD_NAME)
        self.yarrrml_input_file_path = Path(os.path.realpath(yarrrml_input_file))
        self.rml_output_file_path = Path(os.path.realpath(rml_output_file))

        if not self.yarrrml_input_file_path.is_file():
            error_msg = "No such YARRRML file :: [" + yarrrml_input_file + "]"
            self.log_failed_msg(error_msg)
            raise FileNotFoundError(error_msg)

    def run_cmd(self):
        self.convert(self.yarrrml_input_file_path, self.rml_output_file_path)

    def convert(self, yarrrml_input_file_path, rml_output_file_path):
        """
        Converts YARRRML to RML
        """
        self.log("Running " + LOG_INFO_TEXT.format("YARRRML -> RML") + " conversion ... ")

        error = None
        try:
            converter = YARRRML2RMLConverter()
            process = converter.convert(yarrrml_input_file_path, rml_output_file_path)
            if process.returncode != 0:
                raise Exception("Conversion failed :: {error}".format(
                    error=process.stderr.decode("utf-8") if process.stderr else "ERROR")
                )
        except Exception as e:
            error = e

        if error:
            self.log_failed_error(error)
            return False
        else:
            self.log_success_msg()
            return True


@click.command()
@click.argument('mapping-suite-id', nargs=1, required=False)
@click.argument('rml-output-file-name', nargs=1, required=False)
@click.option('-i', '--opt-yarrrml-input-file', help="Use to overwrite INPUT generator")
@click.option('-o', '--opt-rml-output-file', help="Use to overwrite OUTPUT generator")
@click.option('-m', '--opt-mappings-path', default=DEFAULT_MAPPINGS_PATH)
def main(mapping_suite_id, rml_output_file_name, opt_yarrrml_input_file, opt_rml_output_file, opt_mappings_path):
    """
    Converts YARRRML to RML.
    Skip RML_OUTPUT_FILE_NAME to use the default name.
    """

    if opt_yarrrml_input_file:
        yarrrml_input_file = opt_yarrrml_input_file
    else:
        yarrrml_input_file = DEFAULT_YARRRML_INPUT_FILE.format(
            mappings_path=opt_mappings_path,
            mapping_suite_id=mapping_suite_id
        )

    if opt_rml_output_file:
        rml_output_file = opt_rml_output_file
    else:
        rml_output_file = DEFAULT_RML_OUTPUT_FILE.format(
            mappings_path=opt_mappings_path,
            mapping_suite_id=mapping_suite_id,
            output_file_name=rml_output_file_name if rml_output_file_name else DEFAULT_RML_OUTPUT_FILE_NAME
        )

    cmd = CmdRunner(
        yarrrml_input_file=yarrrml_input_file,
        rml_output_file=rml_output_file
    )
    cmd.run()


if __name__ == '__main__':
    main()
