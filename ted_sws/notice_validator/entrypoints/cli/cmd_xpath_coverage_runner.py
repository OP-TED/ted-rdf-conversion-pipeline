#!/usr/bin/python3

import json
import os
from pathlib import Path

import click

from ted_sws.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner, DEFAULT_MAPPINGS_PATH, DEFAULT_OUTPUT_PATH
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.event_manager.adapters.logger import LOG_INFO_TEXT
from ted_sws.mapping_suite_processor.entrypoints.cli import CONCEPTUAL_MAPPINGS_FILE
from ted_sws.notice_validator.services.xpath_coverage_runner import CoverageRunner, coverage_notice_xpath_report

OUTPUT_FOLDER = '{mappings_path}/{mapping_suite_id}/' + DEFAULT_OUTPUT_PATH
DEFAULT_TEST_SUITE_REPORT_FOLDER = "test_suite_report"
JSON_REPORT = "xpath_cov_{id}.json"
CMD_NAME = "CMD_XPATH_COVERAGE_RUNNER"

"""
USAGE:
# xpath_coverage_runner --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Keeps the logic to be used by Coverage Runner
    """

    def __init__(
            self,
            mapping_suite_id,
            conceptual_mappings_file,
            mappings_path,
            xslt_transformer,
            logger=None
    ):
        super().__init__(name=CMD_NAME, logger=logger)
        self.mapping_suite_id = mapping_suite_id
        self.mappings_path = mappings_path
        self.conceptual_mappings_file_path = Path(os.path.realpath(conceptual_mappings_file))
        self.xslt_transformer = xslt_transformer

        if not self.conceptual_mappings_file_path.is_file():
            error_msg = f"No such Conceptual Mappings file :: [{conceptual_mappings_file}]"
            self.log_failed_msg(error_msg)
            raise FileNotFoundError(error_msg)

        repository_path = Path(self.mappings_path)

        mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=repository_path)
        self.mapping_suite = mapping_suite_repository.get(reference=self.mapping_suite_id)
        self.coverage_runner = CoverageRunner(self.conceptual_mappings_file_path)

    def save_report(self, report_path, report_name, notice_id, notice_content):
        json_report = coverage_notice_xpath_report(notice_id, notice_content,
                                                   self.mapping_suite_id, self.conceptual_mappings_file_path,
                                                   self.coverage_runner, self.xslt_transformer)
        with open(report_path / report_name.format(id=notice_id), "w+") as f:
            json.dump(json_report, f, indent=4)
            f.close()

    def coverage_notice(self, notice, output_path):
        notice_id = Path(notice.file_name).stem
        self.log("Generating coverage report for " + LOG_INFO_TEXT.format(notice_id) + " ... ")
        base_report_path = output_path / notice_id
        report_path = base_report_path / DEFAULT_TEST_SUITE_REPORT_FOLDER
        report_path.mkdir(parents=True, exist_ok=True)
        self.save_report(report_path, JSON_REPORT, notice_id, notice.file_content)

    def run_cmd(self):
        output_path = Path(OUTPUT_FOLDER.format(mappings_path=self.mappings_path,
                                                mapping_suite_id=self.mapping_suite_id))
        for notice in self.mapping_suite.transformation_test_data.test_data:
            self.coverage_notice(notice=notice, output_path=output_path)

        return self.run_cmd_result()


def run(mapping_suite_id=None, opt_conceptual_mappings_file=None, opt_mappings_folder=DEFAULT_MAPPINGS_PATH,
        xslt_transformer=None, logger=None):
    if opt_conceptual_mappings_file:
        conceptual_mappings_file = opt_conceptual_mappings_file
    else:
        conceptual_mappings_file = CONCEPTUAL_MAPPINGS_FILE.format(
            mappings_path=opt_mappings_folder,
            mapping_suite_id=mapping_suite_id
        )

    cmd = CmdRunner(
        mapping_suite_id=mapping_suite_id,
        conceptual_mappings_file=conceptual_mappings_file,
        mappings_path=opt_mappings_folder,
        xslt_transformer=xslt_transformer,
        logger=logger
    )
    cmd.run()


@click.command()
@click.argument('mapping-suite-id', nargs=1, required=False)
@click.option('-i', '--opt-conceptual-mappings-file', help="Use to overwrite default INPUT")
@click.option('-m', '--opt-mappings-folder', default=DEFAULT_MAPPINGS_PATH)
def main(mapping_suite_id, opt_conceptual_mappings_file, opt_mappings_folder):
    """
    Generates Coverage Reports for Notices
    """
    run(mapping_suite_id, opt_conceptual_mappings_file, opt_mappings_folder)


if __name__ == '__main__':
    main()
