#!/usr/bin/python3

import json
from pathlib import Path

import click
from ted_sws.event_manager.adapters.log import LOG_WARN_TEXT

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
        self.mapping_suite_ids = self._init_list_input_opts_split(mapping_suite_id)
        self.files = self._init_list_input_opts_split(file)
        self.branches = self._init_list_input_opts_split(branch)
        self.mappings_path = mappings_path
        self.output_folder = output_folder

    def _report(self, diff, files: list):
        data = diff['data']
        report_file_file_name_json = Path(self.output_folder) / (DEFAULT_REPORT_FILE_NAME + ".json")
        with open(report_file_file_name_json, 'w+') as report_file:
            report_file.write(json.dumps(data, indent=2))
        report_file_file_name_html = Path(self.output_folder) / (DEFAULT_REPORT_FILE_NAME + ".html")
        with open(report_file_file_name_html, 'w+') as report_file:
            report_file.write(
                generate_conceptual_mappings_diff_html_report(
                    ConceptualMappingDiff(
                        metadata={
                            "branches": self.branches,
                            "mapping_suite_ids": self.mapping_suite_ids,
                            "files": files,
                            "defaults": diff['metadata']['defaults'],
                            "metadata": diff['metadata']['metadata']
                        },
                        data=data
                    ))
            )

    @classmethod
    def _conceptual_mappings_file_path(cls, mappings_path, mapping_suite_id):
        return CONCEPTUAL_MAPPINGS_FILE_TEMPLATE.format(
            mappings_path=mappings_path,
            mapping_suite_id=mapping_suite_id
        )

    def _mappings_path(self) -> Path:
        mappings_path = Path(self.mappings_path).resolve()
        assert Path(mappings_path).is_dir()
        return mappings_path

    def _display_input(self):
        if self.branches:
            self.log(LOG_WARN_TEXT.format("GIT Branches: ") + str(self.branches))
        if self.mapping_suite_ids:
            self.log(LOG_WARN_TEXT.format("MappingSuites: ") + str(self.mapping_suite_ids))
        if self.files:
            self.log(LOG_WARN_TEXT.format("Files: ") + str(self.files))

    def run_cmd(self):
        self._display_input()

        diff = {}
        filepath1 = None
        filepath2 = None

        file_len = len(self.files)
        mapping_suite_id_len = len(self.mapping_suite_ids)
        branch_len = len(self.branches)

        if not self.branches:
            if self.files and file_len == 2:
                filepath1 = self.files[0]
                assert Path(filepath1).is_file()
                filepath2 = self.files[1]
                assert Path(filepath2).is_file()
            elif self.mapping_suite_ids:
                mappings_path = self._mappings_path()
                if mapping_suite_id_len == 2:
                    filepath1 = self._conceptual_mappings_file_path(mappings_path, self.mapping_suite_ids[0])
                    assert Path(filepath1).is_file()
                    filepath2 = self._conceptual_mappings_file_path(mappings_path, self.mapping_suite_ids[1])
                    assert Path(filepath2).is_file()
                elif mapping_suite_id_len == 1 and file_len == 1:
                    filepath1 = self._conceptual_mappings_file_path(mappings_path, self.mapping_suite_ids[0])
                    assert Path(filepath1).is_file()
                    filepath2 = str(Path(self.files[0]).resolve())
                    assert Path(filepath2).is_file()

        error = None
        if filepath1 and filepath2:
            diff = mapping_suite_diff_files_conceptual_mappings([Path(filepath1), Path(filepath2)])
        elif self.branches:
            assert mapping_suite_id_len > 0
            if branch_len == 1 and mapping_suite_id_len == 1 and not self.files:
                mappings_path = self._mappings_path()
                filepath2 = self._conceptual_mappings_file_path(mappings_path, self.mapping_suite_ids[0])
            else:
                filepath2 = (self.files[0] if file_len == 1 else None)

            diff = mapping_suite_diff_repo_conceptual_mappings(
                branch_or_tag_name=self.branches,
                mapping_suite_id=self.mapping_suite_ids,
                filepath=Path(filepath2) if filepath2 else None
            )
        else:
            error = Exception("Cannot do a diff with provided input!")

        if not error:
            self._report(diff=diff, files=[filepath1, filepath2])

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
@click.option('-ms-id', '--mapping-suite-id', multiple=True, required=False, help="Mapping Suite IDs")
@click.option('-f', '--file', multiple=True, required=False, help="Conceptual Mappings files")
@click.option('-b', '--branch', multiple=True, required=False, help="GIT branches or tags")
@click.option('-m', '--opt-mappings-folder', default=DEFAULT_MAPPINGS_PATH)
@click.option('-o', '--opt-output-folder', default=DEFAULT_REPORT_OUTPUT_FOLDER)
def main(mapping_suite_id, file, branch, opt_mappings_folder, opt_output_folder):
    """
    Generate reports (JSON, HTML) with differences between 2 Conceptual Mappings

    ---

    * --file vs --file:
    # conceptual_mapping_differ --file=<CONCEPTUAL_MAPPINGS_FILE1> --file=<CONCEPTUAL_MAPPINGS_FILE2>

    * --mapping-suite-id vs --file:
    # conceptual_mapping_differ --mapping-suite-id=<MAPPING_SUITE_ID1> --file=<CONCEPTUAL_MAPPINGS_FILE2>

    * --mapping-suite-id vs --mapping-suite-id:
    # conceptual_mapping_differ --mapping-suite-id=<MAPPING_SUITE_ID1> --mapping-suite-id=<MAPPING_SUITE_ID2>

    * --branch + --mapping-suite-id vs --branch + --mapping-suite-id:
    # conceptual_mapping_differ --branch=<BRANCH1>  --mapping-suite-id=<MAPPING_SUITE_ID1> --branch=<BRANCH2> --mapping-suite-id=<MAPPING_SUITE_ID2>
    # conceptual_mapping_differ -b <BRANCH1> -ms-id <MAPPING_SUITE_ID1> -b <BRANCH2> -ms-id <MAPPING_SUITE_ID2>

    * --branch + --mapping-suite-id vs --file:
    # conceptual_mapping_differ --branch=<BRANCH1> --mapping-suite-id=<MAPPING_SUITE_ID1> --file=<FILE2>

    * --branch + --mapping-suite-id (remote) vs --mapping-suite-id (local):
    # conceptual_mapping_differ --branch=<BRANCH> --mapping-suite-id=<MAPPING_SUITE_ID>

    ---

    """
    return run(mapping_suite_id, file, branch, opt_mappings_folder, opt_output_folder)


if __name__ == '__main__':
    main()
