#!/usr/bin/python3

from pathlib import Path

import click

from ted_sws.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner, DEFAULT_MAPPINGS_PATH, DEFAULT_OUTPUT_PATH
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.event_manager.adapters.logger import LOG_INFO_TEXT
from ted_sws.rml_to_html.services.rml_to_html import rml_files_to_html_report

DEFAULT_OUTPUT_FOLDER = '{mappings_path}/{mapping_suite_id}/' + DEFAULT_OUTPUT_PATH
HTML_REPORT = "rml_report.html"
CMD_NAME = "CMD_RML_REPORT_GENERATOR"

"""
USAGE:
# rml_runner --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Keeps the logic to be used by RML Runner
    """

    def __init__(
            self,
            mapping_suite_id,
            mappings_path
    ):
        super().__init__(name=CMD_NAME)
        self.mapping_suite_id = mapping_suite_id
        self.mappings_path = mappings_path

        repository_path = Path(self.mappings_path)
        self.mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=repository_path)

    def save_report(self, report_path, report_name, content):
        with open(report_path / report_name, "w+") as f:
            f.write(content)

    def run_cmd(self):
        error = None
        try:
            if not self.mapping_suite_repository.get(reference=self.mapping_suite_id):
                raise ValueError(f'Not a MappingSuite!')

            self.log("Generating RML report [" + HTML_REPORT + "] for " + LOG_INFO_TEXT.format(self.mapping_suite_id)
                     + " ... ")
            report_path = Path(DEFAULT_OUTPUT_FOLDER.format(mappings_path=self.mappings_path,
                                                            mapping_suite_id=self.mapping_suite_id))
            report_path.mkdir(parents=True, exist_ok=True)
            html_report = rml_files_to_html_report(self.mapping_suite_id, self.mapping_suite_repository)

            self.save_report(report_path, HTML_REPORT, html_report)
        except Exception as e:
            error = e

        return self.run_cmd_result(error)


def run(mapping_suite_id=None, opt_mappings_folder=DEFAULT_MAPPINGS_PATH):
    cmd = CmdRunner(
        mapping_suite_id=mapping_suite_id,
        mappings_path=opt_mappings_folder
    )
    cmd.run()


@click.command()
@click.argument('mapping-suite-id', nargs=1, required=False)
@click.option('-m', '--opt-mappings-folder', default=DEFAULT_MAPPINGS_PATH)
@click.option('-o', '--opt-mappings-folder', default=DEFAULT_MAPPINGS_PATH)
def main(mapping_suite_id, opt_mappings_folder):
    """
    Generates RML modules report file for Mapping Suite.
    """
    run(mapping_suite_id, opt_mappings_folder)


if __name__ == '__main__':
    main()
