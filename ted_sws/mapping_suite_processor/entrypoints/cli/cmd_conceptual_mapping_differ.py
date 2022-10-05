#!/usr/bin/python3

import json
from pathlib import Path

import click

from ted_sws.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner, DEFAULT_MAPPINGS_PATH
from ted_sws.mapping_suite_processor.entrypoints.cli import CONCEPTUAL_MAPPINGS_FILE_TEMPLATE
from ted_sws.mapping_suite_processor.services.conceptual_mapping_differ import \
    mapping_suite_diff_files_conceptual_mappings, mapping_suite_diff_repo_conceptual_mappings, \
    generate_conceptual_mappings_diff_html_report
from ted_sws.core.model.transform import ConceptualMappingDiff

CMD_NAME = "CMD_CONCEPTUAL_MAPPING_DIFFER"

DEFAULT_REPORT_OUTPUT_FOLDER = "."
DEFAULT_REPORT_FILE_NAME = "conceptual_mappings_diff"

"""
USAGE:
# conceptual_mapping_differ --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Keeps the logic to be used by Conceptual Mapping Differ
    1) file vs file
    2) suite vs file
    3) suite vs suite
    4) branch vs suite
    5) branch vs file
    6) branch vs branch
    """

    def __init__(
            self,
            mapping_suite_id,
            mappings_path,
            file,
            branch,
            output_folder
    ):
        super().__init__(name=CMD_NAME)
        self.mapping_suite_id = self._init_list_input_opts_split(mapping_suite_id)
        self.file = self._init_list_input_opts_split(file)
        self.branch = self._init_list_input_opts_split(branch)
        self.mappings_path = mappings_path
        self.output_folder = output_folder

    def _report(self, data):
        report_file_file_name_json = Path(self.output_folder) / (DEFAULT_REPORT_FILE_NAME + ".json")
        with open(report_file_file_name_json, 'w+') as report_file:
            report_file.write(json.dumps(data, indent=2))
        report_file_file_name_html = Path(self.output_folder) / (DEFAULT_REPORT_FILE_NAME + ".html")
        with open(report_file_file_name_html, 'w+') as report_file:
            report_file.write(
                generate_conceptual_mappings_diff_html_report(
                    ConceptualMappingDiff(
                        metadata={
                            "files": self.file,
                            "mapping_suite_ids": self.mapping_suite_id,
                            "branches": self.branch
                        },
                        data=data
                    ))
            )

    def run_cmd(self):
        diff = {}
        filepath1 = None
        filepath2 = None

        file_len = len(self.file)
        if self.file and file_len == 2:
            filepath1 = self.file[0]
            assert Path(filepath1).is_file()
            filepath2 = self.file[1]
            assert Path(filepath2).is_file()
        elif self.mapping_suite_id:
            mappings_path = Path(self.mappings_path).resolve()
            assert Path(mappings_path).is_dir()

            mapping_suite_id_len = len(self.mapping_suite_id)

            if mapping_suite_id_len == 2:
                filepath1 = CONCEPTUAL_MAPPINGS_FILE_TEMPLATE.format(
                    mappings_path=mappings_path,
                    mapping_suite_id=self.mapping_suite_id[0]
                )
                assert Path(filepath1).is_file()
                filepath2 = CONCEPTUAL_MAPPINGS_FILE_TEMPLATE.format(
                    mappings_path=mappings_path,
                    mapping_suite_id=self.mapping_suite_id[1]
                )
                assert Path(filepath2).is_file()
            elif mapping_suite_id_len == 1 and file_len == 1:
                filepath1 = CONCEPTUAL_MAPPINGS_FILE_TEMPLATE.format(
                    mappings_path=mappings_path,
                    mapping_suite_id=self.mapping_suite_id[0]
                )
                assert Path(filepath1).is_file()
                filepath2 = self.file[0]
                assert Path(filepath2).is_file()

        error = None
        if filepath1 and filepath2:
            diff = mapping_suite_diff_files_conceptual_mappings([Path(filepath1), Path(filepath2)])
        elif self.branch:
            mapping_suite_diff_repo_conceptual_mappings(
                branch_or_tag_name=self.branch,
                mapping_suite_id=self.mapping_suite_id,
                filepath=(Path(self.file[0]) if file_len == 1 else None)
            )
        else:
            error = Exception("Cannot do a diff with provided input!")

        self._report(data=diff)
        self.run_cmd_result(error)


def run(mapping_suite_id=None, file=None, branch=None, opt_mappings_folder=DEFAULT_MAPPINGS_PATH,
        opt_output_folder=DEFAULT_REPORT_OUTPUT_FOLDER):
    cmd = CmdRunner(
        mapping_suite_id=mapping_suite_id,
        file=file,
        branch=branch,
        mappings_path=opt_mappings_folder,
        output_folder=opt_output_folder
    )
    return cmd.run()


@click.command()
@click.option('--mapping-suite-id', multiple=True, required=False, help="Mapping Suite IDs")
@click.option('--file', multiple=True, required=False, help="Conceptual Mappings files")
@click.option('--branch', multiple=True, required=False, help="GIT branches or tags")
@click.option('-m', '--opt-mappings-folder', default=DEFAULT_MAPPINGS_PATH)
@click.option('-o', '--opt-output-folder', default=DEFAULT_REPORT_OUTPUT_FOLDER)
def main(mapping_suite_id, file, branch, opt_mappings_folder, opt_output_folder):
    """
    Generate reports (JSON, HTML) with differences between 2 Conceptual Mappings
    """
    return run(mapping_suite_id, file, branch, opt_mappings_folder, opt_output_folder)


if __name__ == '__main__':
    main()
