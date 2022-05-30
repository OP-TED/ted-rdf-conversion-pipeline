import os
from pathlib import Path

import click

from ted_sws.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner, DEFAULT_MAPPINGS_PATH
from ted_sws.data_manager.adapters.mapping_suite_repository import TRANSFORM_PACKAGE_NAME, MAPPINGS_PACKAGE_NAME
from ted_sws.mapping_suite_processor.entrypoints.cli import CONCEPTUAL_MAPPINGS_FILE
from ted_sws.mapping_suite_processor.services.conceptual_mapping_files_injection import \
    mapping_suite_processor_inject_rml_modules as inject_rml_modules
from ted_sws.mapping_suite_processor.services.conceptual_mapping_processor import RML_MODULES_FOLDER
from ted_sws.resources import RESOURCES_PATH

DEFAULT_OUTPUT_PATH = '{mappings_path}/{mapping_suite_id}/' + TRANSFORM_PACKAGE_NAME + '/' + MAPPINGS_PACKAGE_NAME
DEFAULT_RML_MODULES_PATH = RESOURCES_PATH / RML_MODULES_FOLDER
CMD_NAME = "RML_MODULES_INJECTOR"

"""
USAGE:
# rml_modules_injector --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Keeps the logic to be used by RML Modules Injector CMD
    """

    def __init__(
            self,
            conceptual_mappings_file,
            rml_modules_folder,
            output_folder
    ):
        super().__init__(name=CMD_NAME)
        self.conceptual_mappings_file_path = Path(os.path.realpath(conceptual_mappings_file))
        self.rml_modules_folder_path = Path(os.path.realpath(rml_modules_folder))
        self.output_folder_path = Path(os.path.realpath(output_folder))

        if not self.conceptual_mappings_file_path.is_file():
            error_msg = f"No such file :: [{conceptual_mappings_file}]"
            self.log_failed_msg(error_msg)
            raise FileNotFoundError(error_msg)

    def run_cmd(self):
        error = None
        try:
            self.output_folder_path.mkdir(parents=True, exist_ok=True)
            inject_rml_modules(conceptual_mappings_file_path=self.conceptual_mappings_file_path,
                               rml_modules_folder_path=self.rml_modules_folder_path,
                               output_rml_modules_folder_path=self.output_folder_path
                               )
        except Exception as e:
            error = e

        return self.run_cmd_result(error)


def run(mapping_suite_id=None,
        opt_conceptual_mappings_file: str = None,
        opt_output_folder: str = None,
        opt_rml_modules_folder: str = str(DEFAULT_RML_MODULES_PATH),
        opt_mappings_folder=DEFAULT_MAPPINGS_PATH
        ):
    """
    This method will inject the requested RML modules into the MappingSuite
    :param mapping_suite_id:
    :param opt_conceptual_mappings_file:
    :param opt_output_folder:
    :param opt_rml_modules_folder:
    :param opt_mappings_folder:
    :return:
    """
    if opt_conceptual_mappings_file:
        conceptual_mappings_file = opt_conceptual_mappings_file
    else:
        conceptual_mappings_file = CONCEPTUAL_MAPPINGS_FILE.format(
            mappings_path=opt_mappings_folder,
            mapping_suite_id=mapping_suite_id
        )

    rml_modules_folder = opt_rml_modules_folder

    if opt_output_folder and not mapping_suite_id:
        output_folder = opt_output_folder
    else:
        output_folder = DEFAULT_OUTPUT_PATH.format(
            mappings_path=opt_mappings_folder,
            mapping_suite_id=mapping_suite_id
        )

    cmd = CmdRunner(
        conceptual_mappings_file=conceptual_mappings_file,
        rml_modules_folder=rml_modules_folder,
        output_folder=output_folder
    )
    cmd.run()


@click.command()
@click.argument('mapping-suite-id', nargs=1, required=False)
@click.option('-i', '--opt-conceptual-mappings-file', help="Use to overwrite default INPUT")
@click.option('-o', '--opt-output-folder', help="Use to overwrite default OUTPUT")
@click.option('-r', '--opt-rml-modules-folder', default=str(DEFAULT_RML_MODULES_PATH))
@click.option('-m', '--opt-mappings-folder', default=DEFAULT_MAPPINGS_PATH)
def main(mapping_suite_id, opt_conceptual_mappings_file, opt_output_folder, opt_rml_modules_folder,
         opt_mappings_folder):
    """
    Injects the requested RML modules from Conceptual Mappings into the MappingSuite.
    """
    run(mapping_suite_id, opt_conceptual_mappings_file, opt_output_folder, opt_rml_modules_folder, opt_mappings_folder)


if __name__ == '__main__':
    main()
