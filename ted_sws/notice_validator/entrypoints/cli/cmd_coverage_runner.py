#!/usr/bin/python3

from pathlib import Path

import click

from ted_sws.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner, DEFAULT_MAPPINGS_PATH, DEFAULT_OUTPUT_PATH
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.event_manager.adapters.logger import LOG_INFO_TEXT

OUTPUT_FOLDER = '{mappings_path}/{mapping_suite_id}/' + DEFAULT_OUTPUT_PATH
DEFAULT_TEST_SUITE_REPORT_FOLDER = "test_suite_report"
JSON_REPORT = "cov_{id}.html"
CMD_NAME = "CMD_COVERAGE_RUNNER"

"""
USAGE:
# coverage_runner --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Keeps the logic to be used by Coverage Runner
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
        print("SUITE :: ", self.mapping_suite_id)
        print("PATH :: ", self.repository_path)

        mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=repository_path)
        self.mapping_suite = mapping_suite_repository.get(reference=self.mapping_suite_id)

    def save_report(self, report_path, report_name, report_id, content):
        print("NOTICE :: ", report_name.format(id=report_id))
        # with open(report_path / report_name.format(id=report_id), "w+") as f:
        #     f.write(content)

    def coverage_notice(self, notice, base_report_path):
        self.log("Generating coverage report for " + LOG_INFO_TEXT.format(notice.name) + " ... ")
        report_path = base_report_path / DEFAULT_TEST_SUITE_REPORT_FOLDER
        report_path.mkdir(parents=True, exist_ok=True)
        self.save_report(report_path, JSON_REPORT, notice.file_name, notice.file_content)

    def run_cmd(self):
        error = None
        try:
            output_path = Path(OUTPUT_FOLDER.format(mappings_path=self.mappings_path,
                                                    mapping_suite_id=self.mapping_suite_id))
            for notice in self.mapping_suite.transformation_test_data:
                base_report_path = output_path / notice.file_name
                self.coverage_notice(notice=notice, base_report_path=base_report_path)
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
def main(mapping_suite_id, opt_mappings_folder):
    """
    Generates Coverage Reports for Notices
    """
    #run(mapping_suite_id, opt_mappings_folder)


if __name__ == '__main__':
    main()
